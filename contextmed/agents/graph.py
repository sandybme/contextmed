"""
LangGraph ReAct workflow for ContextMed.

Implements Think -> Act -> Observe loop using LangGraph:
- Agent:    MedGemma decides which tool to call (or final_answer)
- Tools:    Execute the selected tool
- Router:   Loops back to Agent or ends if final_answer
"""

from __future__ import annotations

import asyncio
import contextvars
import json
import re
from typing import Any, Callable, Dict, List, Optional, TypedDict, Literal

from langgraph.graph import END, StateGraph

from contextmed.medgemma import MedGemmaClient
from contextmed.models import DoctorContext, PatientEHR, QueryMode
from contextmed.prompts import TOOL_DEFINITIONS, CRITICAL_MODE_PREFIX, STYLE_MAP
from contextmed.tools.guidelines import search_guidelines
from contextmed.tools.openfda import search_openfda
from contextmed.tools.pubmed import search_pubmed
from contextmed.tools.safety import check_allergies, calculate_dose

# ContextVar allows the server to pass a token callback into graph nodes
_token_callback_var: contextvars.ContextVar[Optional[Callable[[str], None]]] = (
    contextvars.ContextVar("_token_callback_var", default=None)
)


# ---------------------------------------------------------------------------
# Agent State
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    # Input
    query: str
    doctor: Dict[str, Any]
    patient: Optional[Dict[str, Any]]
    mode: str
    conversation_context: str

    # ReAct state
    scratchpad: str  # Accumulated Think/Act/Observe history
    current_tool: Optional[str]
    current_params: Optional[Dict]
    tool_results: List[Dict]
    iteration: int

    # Output
    final_response: str
    tools_used: List[str]

    # Injected dependencies
    medgemma: Any
    tavily_api_key: str


# ---------------------------------------------------------------------------
# Node 1: Agent (Think + Decide)
# ---------------------------------------------------------------------------

def agent_node(state: AgentState) -> AgentState:
    """MedGemma thinks and decides which tool to call (or final_answer)."""
    medgemma: MedGemmaClient = state["medgemma"]
    token_callback = _token_callback_var.get()
    query = state["query"]

    # Build the prompt
    prompt = _build_react_prompt(state)

    # Show thinking indicator on first iteration
    if token_callback and state["iteration"] == 0:
        token_callback("🤔 Analyzing query...\n")

    # Generate response
    response = medgemma.generate(prompt, max_tokens=400, stream=False)

    # Parse tool call from response
    tool_name, params = _parse_tool_call(response)

    # Prepare updated state values
    new_scratchpad = state.get("scratchpad", "") + f"\nThought: {response}\n"
    new_tool = tool_name
    new_params = params or {}

    # If no tool was parsed and model didn't explicitly choose final_answer,
    # and query looks clinical, force a guidelines search
    if tool_name is None and state["iteration"] == 0 and not state.get("tools_used"):
        # Check if this looks like a clinical question (let model's response guide us)
        response_lower = response.lower()

        # If model response mentions greeting/hello or query is very short, allow direct answer
        is_conversational = (
            "hello" in response_lower or
            "greeting" in response_lower or
            "how can i help" in response_lower or
            len(state["query"].split()) <= 3
        )

        if not is_conversational:
            if token_callback:
                token_callback("📚 Gathering evidence...\n")
            # Enhance query for critical mode with emergency/critical care context
            search_query = state["query"]
            if state.get("mode") == "critical":
                search_query = f"{search_query} critical care emergency management"
            new_tool = "search_guidelines"
            new_params = {"query": search_query}

    # Return updated state for LangGraph
    return {
        **state,
        "scratchpad": new_scratchpad,
        "current_tool": new_tool,
        "current_params": new_params,
    }


def _build_react_prompt(state: AgentState) -> str:
    """Build the ReAct prompt with context and scratchpad."""
    doctor = state.get("doctor", {})
    patient = state.get("patient")
    mode = state.get("mode", "regular")
    query = state["query"]

    parts = []

    # Critical mode prefix
    if mode == "critical":
        parts.append(CRITICAL_MODE_PREFIX)

    # Tool definitions
    parts.append(TOOL_DEFINITIONS)

    # Doctor context
    experience = doctor.get("experience_level", "attending")
    if hasattr(experience, "value"):
        experience = experience.value
    style = STYLE_MAP.get(experience, STYLE_MAP["attending"])

    parts.append(
        f"\nPHYSICIAN CONTEXT:\n"
        f"- Name: {doctor.get('name', 'Doctor')}\n"
        f"- Specialty: {doctor.get('specialty', 'General')}\n"
        f"- Experience: {experience}\n"
        f"- Country: {doctor.get('country', 'USA')}\n"
        f"- Response style: {style[:100]}..."
    )

    # Patient context
    if patient:
        meds = [m.get("name", "") for m in patient.get("current_medications", [])]
        conditions = [h.get("condition", "") for h in patient.get("medical_history", [])]
        allergies = patient.get("allergies", [])

        labs = patient.get("recent_labs", {})
        labs_abnormal = [
            f"{k}: {v.get('value')}{v.get('unit', '')}"
            for k, v in labs.items()
            if isinstance(v, dict) and v.get("flag") != "N"
        ]

        parts.append(
            f"\nPATIENT:\n"
            f"- {patient.get('age')}yo {patient.get('sex')}, BMI {patient.get('bmi', 'N/A')}\n"
            f"- Chief Complaint: {patient.get('chief_complaint', 'N/A')}\n"
            f"- History: {', '.join(conditions[:5]) or 'None'}\n"
            f"- Medications: {', '.join(meds[:5]) or 'None'}\n"
            f"- ⚠️ ALLERGIES: {', '.join(allergies) or 'NKDA'}\n"
            f"- Abnormal Labs: {', '.join(labs_abnormal[:5]) or 'None'}\n"
            f"- HPI: {patient.get('hpi', '')[:300]}"
        )

    # Conversation context
    conv = state.get("conversation_context", "")
    if conv:
        parts.append(f"\nPREVIOUS CONVERSATION:\n{conv[:500]}")

    # Query
    parts.append(f"\nDOCTOR'S QUESTION: {query}")

    # Scratchpad (accumulated reasoning)
    scratchpad = state.get("scratchpad", "")
    if scratchpad:
        parts.append(f"\n--- Your reasoning so far ---{scratchpad}")

    # Instruction - different for critical vs regular mode
    if state["iteration"] == 0:
        if mode == "critical":
            parts.append(
                "\n\n🚨 CRITICAL MODE - EMERGENCY INSTRUCTIONS:\n"
                "- This is an URGENT clinical situation requiring immediate evidence-based guidance.\n"
                "- ALWAYS search_guidelines with 'critical care' or 'emergency' context added to your query.\n"
                "- Also search_pubmed for recent critical care literature if needed.\n"
                "- Check allergies BEFORE recommending any medications.\n"
                "- Prioritize rapid, actionable recommendations with specific doses.\n\n"
                "Respond with JSON: {\"tool\": \"tool_name\", \"params\": {...}}\n\n"
                "Decide what to do:"
            )
        else:
            parts.append(
                "\n\nINSTRUCTIONS:\n"
                "- For clinical questions (treatment, diagnosis, medications, guidelines), use tools to gather evidence.\n"
                "- For simple greetings or non-clinical conversation, respond directly with final_answer.\n"
                "- For clinical questions, ALWAYS search_guidelines first to get evidence-based recommendations.\n"
                "- If asking about medications, also use search_openfda for drug safety info.\n"
                "- If the patient has allergies, use check_allergies before recommending any medications.\n\n"
                "Respond with JSON: {\"tool\": \"tool_name\", \"params\": {...}}\n"
                "For direct response: {\"tool\": \"final_answer\", \"params\": {\"answer\": \"your response\"}}\n\n"
                "Decide what to do:"
            )
    else:
        parts.append(
            "\n\nBased on the observations above, decide:\n"
            "- Need more info? Call another tool with JSON: {\"tool\": \"...\", \"params\": {...}}\n"
            "- Ready to answer? Use: {\"tool\": \"final_answer\", \"params\": {\"answer\": \"your response\"}}\n\n"
            "Your decision:"
        )

    return "\n".join(parts)


def _parse_tool_call(response: str) -> tuple:
    """Extract tool call JSON from model response."""
    try:
        # Look for JSON with "tool" key
        match = re.search(r'\{[^{}]*"tool"\s*:\s*"[^"]+\"[^{}]*\}', response, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return data.get("tool"), data.get("params", {})
    except Exception:
        pass

    # Only treat as final_answer if explicitly stated
    if "final_answer" in response.lower():
        return "final_answer", {"answer": response}

    # No tool call found - return None to force another iteration
    return None, None


# ---------------------------------------------------------------------------
# Node 2: Tools (Execute)
# ---------------------------------------------------------------------------

def tools_node(state: AgentState) -> AgentState:
    """Execute the selected tool and record observation."""
    tool_name = state.get("current_tool")
    params = state.get("current_params", {})
    patient = state.get("patient")
    doctor = state.get("doctor", {})
    tavily_key = state.get("tavily_api_key", "")
    mode = state.get("mode", "regular")
    token_callback = _token_callback_var.get()

    if not tool_name or tool_name == "final_answer":
        return state

    # Log tool usage to stream
    display_name = _format_tool_name(tool_name)
    if token_callback:
        if mode == "critical":
            token_callback(f"🚨 Searching {display_name} (critical care)...\n")
        else:
            token_callback(f"🔍 Searching {display_name}...\n")

    # Run async tool in sync context
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(
            _execute_tool(tool_name, params, patient, doctor, tavily_key, mode)
        )
    finally:
        loop.close()

    # Log result summary
    if token_callback:
        summary = _summarize_tool_result(tool_name, result)
        if summary:
            token_callback(f"   ✓ {summary}\n")

    # Record observation in scratchpad
    observation = f"Action: {tool_name}({json.dumps(params)})\n"
    observation += f"Observation: {json.dumps(result, default=str)[:600]}\n"
    state["scratchpad"] += observation

    # Track tool usage - create new lists to ensure state updates propagate in LangGraph
    new_tool_results = list(state.get("tool_results", []))
    new_tool_results.append(result)

    new_tools_used = list(state.get("tools_used", []))
    if display_name not in new_tools_used:
        new_tools_used.append(display_name)

    # Return updated state with new list references for LangGraph
    return {
        **state,
        "tool_results": new_tool_results,
        "tools_used": new_tools_used,
        "iteration": state.get("iteration", 0) + 1,
    }


def _summarize_tool_result(tool_name: str, result: Dict) -> str:
    """Generate a brief summary of tool results for display."""
    if tool_name == "search_pubmed":
        count = len(result.get("results", []))
        if count > 0:
            return f"Found {count} relevant studies"
        return "No studies found"

    elif tool_name == "search_openfda":
        results = result.get("results", [])
        if results:
            drugs = [r.get("drug", "") for r in results[:3]]
            return f"Retrieved safety data for: {', '.join(drugs)}"
        return "No drug data found"

    elif tool_name == "search_guidelines":
        count = len(result.get("results", []))
        if count > 0:
            return f"Found {count} clinical guidelines"
        return "No guidelines found"

    elif tool_name == "check_allergies":
        alerts = result.get("alerts", [])
        if alerts:
            return f"⚠️ {len(alerts)} ALLERGY CONFLICT(S) DETECTED"
        return "No allergy conflicts"

    elif tool_name == "calculate_dose":
        if "recommendation" in result:
            return result["recommendation"][:80]
        return "Dose calculated"

    return ""


async def _execute_tool(
    tool_name: str,
    params: dict,
    patient: Optional[Dict],
    doctor: Optional[Dict],
    tavily_api_key: str,
    mode: str = "regular",
) -> Dict:
    """Execute a tool by name and return results."""

    if tool_name == "search_pubmed":
        terms = params.get("terms", params.get("query", "").split())
        # Add critical care terms for critical mode
        if mode == "critical":
            terms = terms + ["critical care", "emergency", "ICU"]
        results = await search_pubmed(terms, max_results=5)
        return {"tool": "search_pubmed", "results": results[:3]}

    elif tool_name == "search_openfda":
        drugs = params.get("drugs", [])
        if isinstance(drugs, str):
            drugs = [drugs]
        results = await search_openfda(drugs)
        return {"tool": "search_openfda", "results": results}

    elif tool_name == "search_guidelines":
        query = params.get("query", "")
        country = params.get("country", doctor.get("country", "USA") if doctor else "USA")
        critical_mode = (mode == "critical")
        results = await search_guidelines(query, country, tavily_api_key, critical_mode=critical_mode)
        return {"tool": "search_guidelines", "results": results[:3]}

    elif tool_name == "check_allergies":
        medications = params.get("medications", [])
        allergies = params.get("allergies", [])
        if not allergies and patient:
            allergies = patient.get("allergies", [])
        alerts = await check_allergies(medications, allergies)
        return {
            "tool": "check_allergies",
            "alerts": [a.model_dump() for a in alerts],
            "has_conflicts": len(alerts) > 0,
        }

    elif tool_name == "calculate_dose":
        drug = params.get("drug", "")
        weight = params.get("weight_kg", patient.get("weight_kg", 70) if patient else 70)
        egfr = params.get("egfr", 90)
        if patient and "eGFR" in patient.get("recent_labs", {}):
            lab = patient["recent_labs"]["eGFR"]
            egfr = lab.get("value", lab) if isinstance(lab, dict) else egfr
        result = await calculate_dose(drug, weight, egfr)
        return {"tool": "calculate_dose", **result}

    return {"tool": tool_name, "error": f"Unknown tool: {tool_name}"}


def _format_tool_name(tool_name: str) -> str:
    """Format tool name for display."""
    name_map = {
        "search_pubmed": "PubMed",
        "search_openfda": "OpenFDA",
        "search_guidelines": "Guidelines",
        "check_allergies": "AllergyCheck",
        "calculate_dose": "DoseCalculator",
    }
    return name_map.get(tool_name, tool_name)


# ---------------------------------------------------------------------------
# Node 3: Final Answer
# ---------------------------------------------------------------------------

def final_answer_node(state: AgentState) -> AgentState:
    """Generate the final clinical response with streaming."""
    medgemma: MedGemmaClient = state["medgemma"]
    token_callback = _token_callback_var.get()

    # Check if we have a pre-computed answer (e.g., greeting)
    params = state.get("current_params", {})
    if params.get("answer") and not state.get("scratchpad"):
        # Direct answer without MedGemma (greetings, simple responses)
        response = params["answer"]
        if token_callback:
            token_callback(response)
        return {**state, "final_response": response}

    # Show summary of evidence gathered
    if token_callback:
        mode = state.get("mode", "regular")
        tools_used = state.get("tools_used", [])

        if mode == "critical":
            token_callback("\n🚨 CRITICAL CARE MODE\n")

        if tools_used:
            token_callback(f"\n📋 Evidence gathered from: {', '.join(tools_used)}\n")
            token_callback("─" * 40 + "\n\n")
        else:
            token_callback("\n")

    # Build final prompt with all gathered evidence
    prompt = _build_final_prompt(state)

    # Stream the final response (same token limit for both modes)
    response = medgemma.generate(
        prompt,
        max_tokens=1024,
        stream=True,
        callback=token_callback,
    )

    # Append citations
    suffix = _build_citations(state)
    if suffix and token_callback:
        token_callback(suffix)

    return {**state, "final_response": response + suffix}


def _build_final_prompt(state: AgentState) -> str:
    """Build the final response prompt with gathered evidence."""
    doctor = state.get("doctor", {})
    patient = state.get("patient")
    mode = state.get("mode", "regular")
    query = state["query"]

    experience = doctor.get("experience_level", "attending")
    if hasattr(experience, "value"):
        experience = experience.value
    style = STYLE_MAP.get(experience, STYLE_MAP["attending"])

    parts = []

    if mode == "critical":
        parts.append(CRITICAL_MODE_PREFIX)

    parts.append(
        f"You are ContextMed, a clinical AI assistant.\n"
        f"Physician: {doctor.get('name')} ({doctor.get('specialty')}, {experience})\n"
        f"Country/Guidelines: {doctor.get('country', 'USA')}\n"
        f"Language: {doctor.get('language', 'English')}\n\n"
        f"{style}"
    )

    # Patient summary
    if patient:
        allergies = patient.get("allergies", [])
        meds = [m.get("name", "") for m in patient.get("current_medications", [])]
        parts.append(
            f"\nPATIENT: {patient.get('age')}yo {patient.get('sex')}\n"
            f"Chief Complaint: {patient.get('chief_complaint')}\n"
            f"⚠️ ALLERGIES: {', '.join(allergies) or 'NKDA'}\n"
            f"Medications: {', '.join(meds[:5]) or 'None'}"
        )

    # Evidence gathered
    if state.get("scratchpad"):
        parts.append(f"\n--- Evidence gathered ---\n{state['scratchpad'][-2000:]}")

    # Query
    parts.append(f"\nDOCTOR'S QUESTION: {query}")

    # Build reference list for the prompt so model knows what to cite
    refs = _collect_references(state)
    if refs:
        parts.append("\n\nAVAILABLE REFERENCES (cite using [1], [2], etc. in your response):")
        for i, ref in enumerate(refs, 1):
            parts.append(f"[{i}] {ref['title'][:80]}")

    parts.append(
        "\n\nProvide your clinical response now. Be specific and actionable.\n"
        "If you found allergy conflicts, warn about them prominently.\n"
        "IMPORTANT: Use numbered citations like [1], [2] when referencing evidence.\n\nResponse:"
    )

    return "\n".join(parts)


def _collect_references(state: AgentState) -> list:
    """Collect references from tool results."""
    refs = []
    for result in state.get("tool_results", []):
        if result.get("tool") == "search_guidelines":
            for r in result.get("results", []):
                refs.append({"title": r.get("title", ""), "url": r.get("url", "")})
        elif result.get("tool") == "search_pubmed":
            for r in result.get("results", []):
                refs.append({"title": r.get("title", ""), "url": r.get("url", "")})
    return refs[:6]  # Limit to 6 references


def _build_citations(state: AgentState) -> str:
    """Build citations from tool results."""
    refs = _collect_references(state)

    if not refs and not state.get("tools_used"):
        return ""

    suffix = "\n\n---\n"
    if refs:
        suffix += "**References:**\n"
        for i, ref in enumerate(refs, 1):
            title = ref['title'][:60] + "..." if len(ref['title']) > 60 else ref['title']
            suffix += f"[{i}] [{title}]({ref['url']})\n"

    if state.get("tools_used"):
        suffix += f"\n*Tools: {', '.join(state['tools_used'])}*"

    return suffix


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

def should_continue(state: AgentState) -> Literal["tools", "final_answer"]:
    """Decide whether to continue tool loop or generate final answer."""
    tool = state.get("current_tool")
    iteration = state.get("iteration", 0)

    # Max iterations reached
    if iteration >= 5:
        return "final_answer"

    # Final answer requested
    if tool == "final_answer" or tool is None:
        return "final_answer"

    # Continue with tools
    return "tools"


# ---------------------------------------------------------------------------
# Build Graph
# ---------------------------------------------------------------------------

def build_agent_graph() -> Any:
    """Build and compile the LangGraph ReAct workflow."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tools_node)
    workflow.add_node("final_answer", final_answer_node)

    # Set entry point
    workflow.set_entry_point("agent")

    # Add conditional edge from agent
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "final_answer": "final_answer",
        }
    )

    # Tools loops back to agent
    workflow.add_edge("tools", "agent")

    # Final answer ends
    workflow.add_edge("final_answer", END)

    return workflow.compile()

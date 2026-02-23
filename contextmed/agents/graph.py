"""
LangGraph agentic workflow for ContextMed.

Pipeline: Planner -> Retriever -> Reasoner -> Formatter
- Planner:   Uses MedGemma to classify intent and decide which tools to run
- Retriever: Runs all selected tools in parallel (async)
- Reasoner:  Generates clinical response grounded in retrieved evidence
- Formatter: Adds safety alerts, citations, and tool metadata
"""

from __future__ import annotations

import asyncio
import contextvars
import json
import re
from typing import Any, Callable, Dict, List, Optional, TypedDict

# ContextVar allows the server to pass a token callback into graph nodes
# without putting it in LangGraph state (which drops callables).
_token_callback_var: contextvars.ContextVar[Optional[Callable[[str], None]]] = (
    contextvars.ContextVar("_token_callback_var", default=None)
)

from langgraph.graph import END, StateGraph

from contextmed.medgemma import MedGemmaClient
from contextmed.models import (
    AllergyAlert,
    Citation,
    ClinicalResponse,
    DoctorContext,
    PatientEHR,
    QueryMode,
)
from contextmed.prompts import (
    INTENT_PROMPT_TEMPLATE,
    build_reasoner_prompt,
)
from contextmed.tools.guidelines import search_guidelines
from contextmed.tools.openfda import search_openfda
from contextmed.tools.pubmed import search_pubmed
from contextmed.tools.safety import check_allergies, calculate_dose


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

    # Planning
    needs_drugs: bool
    needs_literature: bool
    needs_guidelines: bool
    search_terms: List[str]

    # Retrieved evidence
    pubmed_results: List[Dict]
    openfda_results: List[Dict]
    guideline_results: List[Dict]
    allergy_alerts: List[Dict]

    # Output
    final_response: str
    citations: List[Dict]
    tools_used: List[str]

    # Injected dependencies
    medgemma: Any
    tavily_api_key: str


# ---------------------------------------------------------------------------
# Node 1: Planner
# ---------------------------------------------------------------------------

def planner_node(state: AgentState) -> AgentState:
    """Analyse query and decide which tools to run using MedGemma."""
    medgemma: MedGemmaClient = state["medgemma"]
    query = state["query"]
    has_patient = state.get("patient") is not None

    # Use MedGemma to classify intent
    prompt = INTENT_PROMPT_TEMPLATE.format(
        query=query,
        has_patient="Yes" if has_patient else "No",
    )

    try:
        resp = medgemma.generate(prompt, max_tokens=120, stream=False)
        match = re.search(r"\{[^{}]+\}", resp)
        if match:
            intent = json.loads(match.group())
            state["needs_drugs"] = intent.get("needs_drugs", False) or has_patient
            state["needs_literature"] = intent.get("needs_literature", True)
            state["needs_guidelines"] = intent.get("needs_guidelines", True)
            terms = intent.get("search_terms", [])
            state["search_terms"] = terms if terms else query.split()[:5]
        else:
            raise ValueError("No JSON found")
    except Exception:
        state["needs_drugs"] = has_patient
        state["needs_literature"] = True
        state["needs_guidelines"] = True
        state["search_terms"] = query.split()[:5]

    return state


# ---------------------------------------------------------------------------
# Node 2: Retriever (async, parallel)
# ---------------------------------------------------------------------------

def retriever_node(state: AgentState) -> AgentState:
    """Run all selected tools in parallel."""
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(_retrieve_async(state))
    finally:
        loop.close()
    return result


async def _retrieve_async(state: AgentState) -> AgentState:
    """Async retrieval of all evidence sources."""
    tasks = []
    task_names: List[str] = []

    patient = state.get("patient")
    doctor = state.get("doctor", {})
    country = doctor.get("country", "USA")
    terms = state.get("search_terms", [])
    tavily_key = state.get("tavily_api_key", "")

    if state.get("needs_literature") and terms:
        tasks.append(search_pubmed(terms))
        task_names.append("pubmed")

    if state.get("needs_drugs") and patient:
        meds = [m.get("name", "") for m in patient.get("current_medications", [])]
        if meds:
            tasks.append(search_openfda(meds))
            task_names.append("openfda")

    if state.get("needs_guidelines") and terms:
        query = " ".join(terms[:3])
        tasks.append(search_guidelines(query, country, tavily_key))
        task_names.append("guidelines")

    if patient:
        meds = [m.get("name", "") for m in patient.get("current_medications", [])]
        allergies = patient.get("allergies", [])
        if meds and allergies:
            tasks.append(check_allergies(meds, allergies))
            task_names.append("allergy")

    tools_used: List[str] = []

    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, name in enumerate(task_names):
            result = results[i] if not isinstance(results[i], Exception) else []
            # Convert AllergyAlert objects to dicts if needed
            if name == "allergy" and result:
                result = [
                    a.model_dump() if hasattr(a, "model_dump") else a
                    for a in result
                ]
            if name == "pubmed":
                state["pubmed_results"] = result
                if result:
                    tools_used.append("PubMed")
            elif name == "openfda":
                state["openfda_results"] = result
                if result:
                    tools_used.append("OpenFDA")
            elif name == "guidelines":
                state["guideline_results"] = result
                if result:
                    tools_used.append("Guidelines")
            elif name == "allergy":
                state["allergy_alerts"] = result
                if result:
                    tools_used.append("AllergyCheck")

    state["tools_used"] = tools_used
    return state


# ---------------------------------------------------------------------------
# Node 3: Reasoner
# ---------------------------------------------------------------------------

def reasoner_node(state: AgentState) -> AgentState:
    """Generate clinical response using MedGemma grounded in retrieved evidence."""
    medgemma: MedGemmaClient = state["medgemma"]
    doctor_dict = state.get("doctor", {})
    patient_dict = state.get("patient")
    token_callback = _token_callback_var.get()

    # Stream allergy alerts before LLM generation so they appear first
    alerts = state.get("allergy_alerts", [])
    if alerts and token_callback:
        warning_lines = ["## ALLERGY ALERTS"]
        for a in alerts:
            drug = a.get("drug", "")
            allergy = a.get("allergy", "")
            warning_lines.append(f"- **{drug}** — Patient allergic to {allergy}!")
        warning_lines.append("\n---\n")
        token_callback("\n".join(warning_lines))

    # Reconstruct Pydantic models for prompt building
    doctor = DoctorContext(**doctor_dict)
    patient = PatientEHR(**patient_dict) if patient_dict else None
    mode = QueryMode(state.get("mode", "regular"))

    prompt = build_reasoner_prompt(
        query=state["query"],
        doctor=doctor,
        patient=patient,
        allergy_alerts=state.get("allergy_alerts"),
        guideline_results=state.get("guideline_results"),
        pubmed_results=state.get("pubmed_results"),
        openfda_results=state.get("openfda_results"),
        mode=mode,
    )

    # Add conversation context if available
    conv_context = state.get("conversation_context", "")
    if conv_context:
        prompt = conv_context + "\n\n" + prompt

    max_tokens = 150 if mode == QueryMode.CRITICAL else 1024
    state["final_response"] = medgemma.generate(
        prompt,
        max_tokens=max_tokens,
        stream=False,
        callback=token_callback,
    )

    return state


# ---------------------------------------------------------------------------
# Node 4: Formatter
# ---------------------------------------------------------------------------

def formatter_node(state: AgentState) -> AgentState:
    """Add safety alerts, citations, and metadata to the response."""
    response = state.get("final_response", "")
    token_callback = _token_callback_var.get()

    # Prepend allergy warnings
    alerts = state.get("allergy_alerts", [])
    if alerts:
        warning_lines = ["## ALLERGY ALERTS"]
        for a in alerts:
            drug = a.get("drug", "")
            allergy = a.get("allergy", "")
            warning_lines.append(f"- **{drug}** — Patient allergic to {allergy}!")
        warning_lines.append("\n---\n")
        prefix = "\n".join(warning_lines)
        response = prefix + response

    # Append citations
    citations: List[Dict] = []
    for r in state.get("guideline_results", [])[:3]:
        citations.append({"title": r["title"][:60], "url": r["url"], "source": "guidelines"})
    for r in state.get("pubmed_results", [])[:3]:
        citations.append({"title": r["title"][:60], "url": r["url"], "source": "pubmed"})

    suffix = ""
    if citations:
        suffix += "\n\n---\n## References\n"
        for i, c in enumerate(citations, 1):
            suffix += f"{i}. [{c['title']}]({c['url']})\n"

    # Tools used footer
    tools = state.get("tools_used", [])
    if tools:
        suffix += f"\n*Tools used: {', '.join(tools)}*"

    if suffix:
        if token_callback:
            token_callback(suffix)
        response += suffix

    state["final_response"] = response
    state["citations"] = citations
    return state


# ---------------------------------------------------------------------------
# Build Graph
# ---------------------------------------------------------------------------

def build_agent_graph() -> Any:
    """Build and compile the LangGraph agentic workflow."""
    workflow = StateGraph(AgentState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("reasoner", reasoner_node)
    workflow.add_node("formatter", formatter_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "retriever")
    workflow.add_edge("retriever", "reasoner")
    workflow.add_edge("reasoner", "formatter")
    workflow.add_edge("formatter", END)

    return workflow.compile()

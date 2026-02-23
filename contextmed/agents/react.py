"""
ReAct Agent for ContextMed.

Implements the Think -> Act -> Observe -> Loop pattern where
MedGemma decides which tools to call autonomously.
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Callable, Dict, List, Optional

from contextmed.medgemma import MedGemmaClient
from contextmed.models import DoctorContext, PatientEHR, QueryMode
from contextmed.prompts import TOOL_DEFINITIONS, CRITICAL_MODE_PREFIX


async def _execute_tool(
    tool_name: str,
    params: dict,
    patient: Optional[Dict] = None,
    doctor: Optional[Dict] = None,
    tavily_api_key: str = "",
) -> Dict:
    """Execute a tool by name and return results."""
    from contextmed.tools.pubmed import search_pubmed
    from contextmed.tools.openfda import search_openfda
    from contextmed.tools.guidelines import search_guidelines
    from contextmed.tools.safety import check_allergies, calculate_dose

    if tool_name == "search_pubmed":
        terms = params.get("terms", [])
        max_results = params.get("max_results", 5)
        results = await search_pubmed(terms, max_results)
        return {"tool": "search_pubmed", "results": results}

    elif tool_name == "search_openfda":
        drugs = params.get("drugs", [])
        results = await search_openfda(drugs)
        return {"tool": "search_openfda", "results": results}

    elif tool_name == "search_guidelines":
        query = params.get("query", "")
        country = params.get(
            "country",
            doctor.get("country", "USA") if doctor else "USA",
        )
        results = await search_guidelines(query, country, tavily_api_key)
        return {"tool": "search_guidelines", "results": results}

    elif tool_name == "check_allergies":
        medications = params.get("medications", [])
        allergies = params.get("allergies", [])
        if not allergies and patient:
            allergies = patient.get("allergies", [])
        alerts = await check_allergies(medications, allergies)
        return {
            "tool": "check_allergies",
            "results": [a.model_dump() for a in alerts],
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

    elif tool_name == "final_answer":
        return {"tool": "final_answer", "answer": params.get("answer", "")}

    return {"tool": "unknown", "error": f"Unknown tool: {tool_name}"}


def _parse_tool_call(response: str):
    """Extract tool call JSON from model response."""
    try:
        match = re.search(r'\{[^{}]*"tool"[^{}]*\}', response, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return data.get("tool"), data.get("params", {})
    except Exception:
        pass
    return None, None


async def react_agent(
    query: str,
    medgemma: MedGemmaClient,
    doctor: Dict,
    patient: Optional[Dict] = None,
    tavily_api_key: str = "",
    max_iterations: int = 5,
    max_response_tokens: int = 500,
    conversation_history: Optional[List[Dict]] = None,
    mode: str = "regular",
    callback: Optional[Callable[[str], None]] = None,
) -> str:
    """
    ReAct Agent: Model decides which tools to call.

    Think -> Act -> Observe -> Think -> ... -> Final Answer
    """
    # Build initial context
    context_parts = [TOOL_DEFINITIONS]

    if mode == "critical":
        context_parts.insert(0, CRITICAL_MODE_PREFIX)

    # Doctor context
    experience = doctor.get("experience_level", "attending")
    if hasattr(experience, "value"):
        experience = experience.value

    context_parts.append(
        f"\nPHYSICIAN CONTEXT:\n"
        f"- Name: {doctor.get('name', 'Doctor')}\n"
        f"- Specialty: {doctor.get('specialty', 'General')}\n"
        f"- Experience: {experience}\n"
        f"- Country: {doctor.get('country', 'USA')}"
    )

    # Patient context
    if patient:
        meds = [m.get("name", "") for m in patient.get("current_medications", [])]
        conditions = [h.get("condition", "") for h in patient.get("medical_history", [])]
        labs = patient.get("recent_labs", {})
        labs_abnormal = [
            f"{k}: {v.get('value')}{v.get('unit', '')}"
            for k, v in labs.items()
            if isinstance(v, dict) and v.get("flag") != "N"
        ]

        context_parts.append(
            f"\nPATIENT CONTEXT:\n"
            f"- {patient.get('age')}yo {patient.get('sex')}, BMI {patient.get('bmi', 'N/A')}\n"
            f"- Chief Complaint: {patient.get('chief_complaint', 'N/A')}\n"
            f"- Medical History: {', '.join(conditions[:5])}\n"
            f"- Current Medications: {', '.join(meds[:5])}\n"
            f"- ALLERGIES: {', '.join(patient.get('allergies', [])) or 'NKDA'}\n"
            f"- Abnormal Labs: {', '.join(labs_abnormal[:5]) or 'None'}\n"
            f"- HPI: {patient.get('hpi', '')[:300]}"
        )

    # Conversation history
    if conversation_history:
        history_text = "\nPREVIOUS CONVERSATION:\n"
        for msg in conversation_history[-6:]:
            role = "Doctor" if msg.get("role") == "user" else "Assistant"
            history_text += f"{role}: {msg.get('content', '')[:200]}\n"
        context_parts.append(history_text)

    context_parts.append(
        f"\nDOCTOR'S QUESTION: {query}\n\n"
        f"Think step by step. What information do you need?\n"
        f"Start by calling appropriate tools, then provide final_answer.\n\n"
        f"Think:"
    )

    conversation = "\n".join(context_parts)

    # ReAct loop
    for iteration in range(max_iterations):
        if callback:
            callback(f"\n[Iteration {iteration + 1}] Thinking...\n")

        response = medgemma.generate(
            conversation, max_tokens=max_response_tokens, stream=False
        )

        if callback:
            callback(f"Model: {response[:200]}...\n")

        tool_name, params = _parse_tool_call(response)

        if tool_name == "final_answer":
            final = params.get("answer", response)
            if callback:
                callback("\n[FINAL ANSWER]\n")
            return final

        elif tool_name:
            if callback:
                callback(f"[Calling tool: {tool_name}]\n")
            try:
                result = await _execute_tool(
                    tool_name, params, patient, doctor, tavily_api_key
                )
                observation = (
                    f"\nObservation from {tool_name}: "
                    f"{json.dumps(result, indent=2, default=str)[:500]}"
                )
                conversation += (
                    f"\n{response}\n{observation}\n\n"
                    f"Think about what you learned and what to do next:\nThink:"
                )
                if callback:
                    callback("[Tool result received]\n")
            except Exception as e:
                conversation += (
                    f"\n{response}\nObservation: Tool error - {e}\n\nThink:"
                )
        else:
            conversation += (
                f"\n{response}\n\n"
                f"You must call a tool or provide final_answer. Choose a tool:\nThink:"
            )

    # Max iterations — force final answer
    if callback:
        callback("\n[Max iterations reached — generating final answer]\n")

    final_prompt = (
        conversation
        + "\n\nYou've gathered enough information. "
        "Now provide your final_answer with a complete clinical response."
    )
    return medgemma.generate(final_prompt, max_tokens=max_response_tokens, stream=False)

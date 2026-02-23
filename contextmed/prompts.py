"""
Prompt templates for ContextMed.

All prompts are geography-aware, experience-adaptive, and context-grounded.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from contextmed.models import DoctorContext, PatientEHR, QueryMode


# ---------------------------------------------------------------------------
# Experience-level response style instructions
# ---------------------------------------------------------------------------

STYLE_MAP = {
    "student": (
        "You are teaching a medical student. Provide detailed explanations with:\n"
        "- Pathophysiology and mechanisms\n"
        "- Step-by-step clinical reasoning\n"
        "- Key learning points and pearls\n"
        "- Common mistakes to avoid"
    ),
    "resident": (
        "You are consulting with a resident physician. Focus on:\n"
        "- Clinical decision-making frameworks\n"
        "- Key decision points and branch logic\n"
        "- Evidence-based reasoning\n"
        "- When to escalate or seek attending input"
    ),
    "attending": (
        "You are assisting an attending physician. Be:\n"
        "- Concise and action-oriented\n"
        "- Focused on critical findings and immediate next steps\n"
        "- Specific with recommendations\n"
        "- Including relevant evidence when it changes management"
    ),
    "senior": (
        "You are supporting a senior physician. Provide:\n"
        "- Brief, focused summary\n"
        "- Only critical or unusual points\n"
        "- New evidence that might change practice\n"
        "- Safety alerts only when significant"
    ),
}


CRITICAL_MODE_PREFIX = """CRITICAL CARE MODE

STRICT FORMAT - EXACTLY 4 LINES:
Line 1: Assessment (diagnosis/condition with key finding)
Line 2: Immediate action (drug + exact dose OR intervention)
Line 3: Monitor (specific parameter + target value)
Line 4: Context-aware question (ask what you need to know for next step)

RULES:
- Pack ALL critical info into 4 lines - be dense but clear
- ALWAYS end with a relevant follow-up question based on patient context
- Use patient data (allergies, meds, labs) to personalise your question

"""


# ---------------------------------------------------------------------------
# Tool definition prompt for ReAct agent
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = """You have access to the following tools. To use a tool, respond with JSON:
{"tool": "tool_name", "params": {"param1": "value1"}}

AVAILABLE TOOLS:

1. search_pubmed
   Search PubMed for medical research papers and clinical studies.
   Params: {"terms": ["search", "terms"], "max_results": 5}

2. search_openfda
   Get FDA drug information including warnings, interactions, contraindications.
   Params: {"drugs": ["drug1", "drug2"]}

3. search_guidelines
   Search for clinical practice guidelines (ACC, AHA, ESC, AWMF, etc.).
   Params: {"query": "search query", "country": "USA|Germany|EU|India|UK"}

4. check_allergies
   Check if medications conflict with patient allergies.
   Params: {"medications": ["med1"], "allergies": ["allergy1"]}

5. calculate_dose
   Calculate weight/renal-adjusted medication dosing.
   Params: {"drug": "drug_name", "weight_kg": 70, "egfr": 60}

6. final_answer
   Provide your final response to the doctor.
   Params: {"answer": "your complete clinical response"}

INSTRUCTIONS:
- Think step by step about what information you need.
- Call tools one at a time, observe results, then decide next action.
- Always check allergies before recommending medications.
- Use final_answer when ready to respond.
"""


# ---------------------------------------------------------------------------
# Intent classification prompt
# ---------------------------------------------------------------------------

INTENT_PROMPT_TEMPLATE = """Analyse this medical query. Respond with ONLY JSON, no other text.

Query: "{query}"
Has patient context: {has_patient}

JSON format:
{{"needs_drugs": true/false, "needs_literature": true/false, "needs_guidelines": true/false, "search_terms": ["term1", "term2", "term3"]}}

needs_drugs = asking about medications, doses, drug interactions, side effects
needs_literature = asking about evidence, studies, research, pathophysiology
needs_guidelines = asking about treatment protocols, management plans, clinical recommendations

JSON:"""


# ---------------------------------------------------------------------------
# Builder functions
# ---------------------------------------------------------------------------

def build_system_prompt(
    doctor: DoctorContext,
    patient: Optional[PatientEHR] = None,
    mode: QueryMode = QueryMode.REGULAR,
) -> str:
    """Build the system-level context prompt for MedGemma."""

    experience = doctor.experience_level.value
    style = STYLE_MAP.get(experience, STYLE_MAP["attending"])

    parts: List[str] = []

    if mode == QueryMode.CRITICAL:
        parts.append(CRITICAL_MODE_PREFIX)

    parts.append(
        f"You are ContextMed, a clinical AI assistant.\n\n"
        f"YOUR PRIMARY ROLE: Support THIS doctor's clinical decision-making.\n"
        f"- Tailor to specialty ({doctor.specialty}) and experience ({experience})\n"
        f"- Use language appropriate for {doctor.country} clinical practice\n"
        f"- Respond in {doctor.language}\n\n"
        f"{style}"
    )

    # Doctor identity
    parts.append(
        f"\nCONSULTING PHYSICIAN:\n"
        f"- Name: {doctor.name}\n"
        f"- Specialty: {doctor.specialty}\n"
        f"- Experience: {experience}\n"
        f"- Setting: {doctor.workplace_type}\n"
        f"- Country/Guidelines: {doctor.country}"
    )

    # Patient context
    if patient:
        parts.append(_build_patient_context(patient))

    return "\n".join(parts)


def _build_patient_context(patient: PatientEHR) -> str:
    """Format patient data into a concise clinical summary."""
    meds = ", ".join(
        f"{m.name} {m.dose}" for m in patient.current_medications[:5]
    )
    conditions = ", ".join(
        h.condition for h in patient.medical_history[:5]
    )
    labs_abnormal = [
        f"{k}: {v.value}{v.unit} ({v.flag})"
        for k, v in patient.recent_labs.items()
        if v.flag != "N"
    ]
    vitals_str = ", ".join(
        f"{k}: {v}" for k, v in patient.recent_vitals.items()
    )

    return (
        f"\nYOUR PATIENT:\n"
        f"- Demographics: {patient.age}yo {patient.sex}, BMI {patient.bmi}\n"
        f"- Chief Complaint: {patient.chief_complaint}\n"
        f"- Medical History: {conditions}\n"
        f"- Current Medications: {meds}\n"
        f"- ALLERGIES: {', '.join(patient.allergies) or 'NKDA'}\n"
        f"- Vitals: {vitals_str or 'Not available'}\n"
        f"- Abnormal Labs: {', '.join(labs_abnormal[:5]) or 'None flagged'}\n"
        f"- HPI: {patient.hpi}"
    )


def build_reasoner_prompt(
    query: str,
    doctor: DoctorContext,
    patient: Optional[PatientEHR],
    allergy_alerts: List[Dict] = None,
    guideline_results: List[Dict] = None,
    pubmed_results: List[Dict] = None,
    openfda_results: List[Dict] = None,
    mode: QueryMode = QueryMode.REGULAR,
) -> str:
    """Build the full prompt for the reasoner node, including retrieved evidence."""

    parts: List[str] = [build_system_prompt(doctor, patient, mode)]

    # Safety alerts
    if allergy_alerts:
        parts.append("\nCRITICAL ALLERGY ALERTS:")
        for a in allergy_alerts:
            drug = a.get("drug", a) if isinstance(a, dict) else a.drug
            allergy = a.get("allergy", "") if isinstance(a, dict) else a.allergy
            parts.append(f"  - {drug} conflicts with allergy to {allergy}")

    # Guidelines
    if guideline_results:
        parts.append("\nRELEVANT GUIDELINES:")
        for r in guideline_results[:3]:
            parts.append(f"  - {r['title'][:80]}")
            if r.get("content"):
                parts.append(f"    {r['content'][:200]}")

    # Literature
    if pubmed_results:
        parts.append("\nRECENT LITERATURE:")
        for r in pubmed_results[:3]:
            parts.append(
                f"  - {r['title'][:80]} ({r.get('source', '')}, {r.get('pubdate', '')})"
            )

    # Drug safety
    if openfda_results:
        parts.append("\nDRUG SAFETY INFO:")
        for r in openfda_results[:3]:
            parts.append(f"  - {r['drug'].title()}: See warnings/interactions")

    # Query
    experience = doctor.experience_level.value
    parts.append(
        f"\n---\nDOCTOR'S QUESTION: {query}\n---\n\n"
        f"Provide a structured clinical response:\n"
        f"1. ASSESSMENT — Key clinical findings\n"
        f"2. DIFFERENTIAL / DIAGNOSIS\n"
        f"3. RECOMMENDATIONS — Specific next steps\n"
        f"4. SAFETY CONSIDERATIONS\n"
        f"5. FOLLOW-UP\n\n"
        f"Response:"
    )

    return "\n".join(parts)

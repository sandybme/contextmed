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


CRITICAL_MODE_PREFIX = """CRITICAL CARE MODE - EMERGENCY RESPONSE

FORMAT: Provide a rapid, actionable response in this exact structure:
1. **Assessment**: Primary diagnosis/condition with key supporting finding
2. **Immediate Action**: Specific intervention with exact drug/dose OR procedure
3. **Monitor**: Parameter to watch + target value + frequency
4. **Safety Alert**: Critical consideration based on patient's specific context

Keep response dense but clear. Use patient's allergies, medications, and labs to personalize.
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
        f"\n═══════════════════════════════════════════════════════════════\n"
        f"PATIENT ELECTRONIC HEALTH RECORD (EHR)\n"
        f"═══════════════════════════════════════════════════════════════\n"
        f"Patient: {patient.name} | ID: {patient.patient_id}\n"
        f"Demographics: {patient.age}yo {patient.sex}, BMI {patient.bmi:.1f}, {patient.weight_kg}kg\n"
        f"Insurance: {patient.insurance}\n\n"
        f"CHIEF COMPLAINT:\n{patient.chief_complaint}\n\n"
        f"HISTORY OF PRESENT ILLNESS (HPI):\n{patient.hpi}\n\n"
        f"MEDICAL HISTORY:\n{conditions or 'None documented'}\n\n"
        f"CURRENT MEDICATIONS:\n{meds or 'None'}\n\n"
        f"⚠️  ALLERGIES: {', '.join(patient.allergies) if patient.allergies else 'NKDA (No Known Drug Allergies)'}\n\n"
        f"VITAL SIGNS:\n{vitals_str or 'Not available'}\n\n"
        f"ABNORMAL LABORATORY VALUES:\n{chr(10).join(labs_abnormal[:5]) if labs_abnormal else 'All within normal limits'}\n"
        f"═══════════════════════════════════════════════════════════════"
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

    # Safety alerts - these are critical
    if allergy_alerts:
        parts.append("\n🚨 CRITICAL ALLERGY ALERTS:")
        for a in allergy_alerts:
            drug = a.get("drug", a) if isinstance(a, dict) else a.drug
            allergy = a.get("allergy", "") if isinstance(a, dict) else a.allergy
            parts.append(f"  ⚠️  {drug} — CONTRAINDICATED due to {allergy} allergy")

    # Evidence section
    has_evidence = guideline_results or pubmed_results or openfda_results
    if has_evidence:
        parts.append("\n───────────────────────────────────────────────────────────────")
        parts.append("RETRIEVED EVIDENCE (use to support your recommendations)")
        parts.append("───────────────────────────────────────────────────────────────")

    # Guidelines
    if guideline_results:
        parts.append("\n📋 CLINICAL GUIDELINES:")
        for r in guideline_results[:3]:
            parts.append(f"  • {r['title'][:80]}")
            if r.get("content"):
                parts.append(f"    Summary: {r['content'][:200]}...")

    # Literature
    if pubmed_results:
        parts.append("\n📚 RECENT LITERATURE:")
        for r in pubmed_results[:3]:
            parts.append(
                f"  • {r['title'][:80]} ({r.get('source', 'PubMed')}, {r.get('pubdate', '')})"
            )

    # Drug safety
    if openfda_results:
        parts.append("\n💊 DRUG SAFETY INFORMATION:")
        for r in openfda_results[:3]:
            parts.append(f"  • {r['drug'].title()}: Review warnings and interactions")

    # The actual question section - clearly separated
    parts.append("\n\n" + "═" * 67)
    parts.append("DOCTOR'S QUESTION")
    parts.append("═" * 67)
    parts.append(f"\n{query}\n")
    parts.append("═" * 67)

    # Instructions based on mode
    if mode == QueryMode.CRITICAL:
        parts.append(
            "\nProvide an EMERGENCY response following the critical care format above.\n"
            "Be specific with doses and interventions. Consider patient's allergies and current medications."
        )
    else:
        parts.append(
            "\n📝 INSTRUCTIONS:\n"
            "Answer the doctor's specific question above. Do NOT provide a general overview of the patient.\n"
            "Focus ONLY on what was asked. Use the patient's EHR data and retrieved evidence to inform your response.\n\n"
            "Structure your response based on what's being asked:\n"
            "- For diagnosis questions: Present differentials with reasoning\n"
            "- For treatment questions: Provide specific recommendations with evidence\n"
            "- For management plans: Outline concrete next steps\n"
            "- For medication questions: Include doses, contraindications, monitoring\n\n"
            "Always consider:\n"
            "• Patient's specific allergies and contraindications\n"
            "• Current medications and potential interactions\n"
            "• Relevant lab values and vital signs\n"
            "• Evidence from guidelines and literature when available"
        )

    parts.append("\n\nResponse:")

    return "\n".join(parts)

"""
ContextMed Agent — the main orchestrator.

Provides a simple interface to:
  1. Set doctor/patient context
  2. Query via the LangGraph pipeline or ReAct agent
  3. Manage conversation memory
  4. Dynamically create doctors/patients
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from contextmed.agents.graph import AgentState, build_agent_graph
from contextmed.config import Settings, load_settings
from contextmed.data.personas import ALL_PATIENTS, DOCTOR_PERSONAS
from contextmed.medgemma import MedGemmaClient
from contextmed.memory import ClinicalNotepad, ConversationMemory
from contextmed.models import (
    DoctorContext,
    ExperienceLevel,
    Medication,
    MedicalCondition,
    PatientEHR,
    QueryMode,
)


class ContextMedAgent:
    """High-level agent interface for ContextMed."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        medgemma: Optional[MedGemmaClient] = None,
    ):
        self.settings = settings or load_settings()
        self.medgemma = medgemma or MedGemmaClient(self.settings)

        self.graph = build_agent_graph()
        self.memory = ConversationMemory()
        self.notepad = ClinicalNotepad()

        self.doctors = dict(DOCTOR_PERSONAS)
        self.patients = dict(ALL_PATIENTS)

        self._current_doctor: Optional[DoctorContext] = None
        self._current_patient: Optional[PatientEHR] = None

    # ------------------------------------------------------------------
    # Model lifecycle
    # ------------------------------------------------------------------

    def load_model(self) -> None:
        """Load MedGemma onto GPU."""
        from huggingface_hub import login

        if self.settings.hf_token:
            login(token=self.settings.hf_token)
        self.medgemma.load()

    # ------------------------------------------------------------------
    # Doctor / Patient selection
    # ------------------------------------------------------------------

    def set_doctor(self, doctor_id: str) -> str:
        if doctor_id in self.doctors:
            self._current_doctor = self.doctors[doctor_id]
            return f"Doctor set: {self._current_doctor.name} ({self._current_doctor.specialty})"
        return f"Not found. Options: {list(self.doctors.keys())}"

    def set_patient(self, patient_id: str) -> str:
        if patient_id in self.patients:
            self._current_patient = self.patients[patient_id]
            return f"Patient set: {self._current_patient.name} — {self._current_patient.chief_complaint}"
        return f"Not found. Options: {list(self.patients.keys())}"

    @property
    def doctor(self) -> Optional[DoctorContext]:
        return self._current_doctor

    @property
    def patient(self) -> Optional[PatientEHR]:
        return self._current_patient

    # ------------------------------------------------------------------
    # Query (LangGraph pipeline)
    # ------------------------------------------------------------------

    def query(self, query: str, mode: str = "regular") -> str:
        """Run a clinical query through the LangGraph pipeline."""
        if not self._current_doctor:
            return "Please set a doctor first: agent.set_doctor('usa_er_attending')"

        # Retrieve conversation context
        patient_id = self._current_patient.patient_id if self._current_patient else ""
        conv_context = self.memory.format_for_prompt(
            self._current_doctor.id, patient_id
        )

        # Build initial state
        state: AgentState = {
            "query": query,
            "doctor": self._current_doctor.model_dump(),
            "patient": self._current_patient.model_dump() if self._current_patient else None,
            "mode": mode,
            "conversation_context": conv_context,
            "needs_drugs": False,
            "needs_literature": False,
            "needs_guidelines": False,
            "search_terms": [],
            "pubmed_results": [],
            "openfda_results": [],
            "guideline_results": [],
            "allergy_alerts": [],
            "final_response": "",
            "citations": [],
            "tools_used": [],
            "medgemma": self.medgemma,
            "tavily_api_key": self.settings.tavily_api_key,
        }

        result = self.graph.invoke(state)

        # Store in memory
        self.memory.add(self._current_doctor.id, "user", query, patient_id)
        self.memory.add(
            self._current_doctor.id,
            "assistant",
            result["final_response"][:500],
            patient_id,
        )

        return result["final_response"]

    # ------------------------------------------------------------------
    # Dynamic creation
    # ------------------------------------------------------------------

    def create_doctor(
        self,
        name: str,
        specialty: str,
        experience_level: str,
        country: str = "USA",
        workplace_type: str = "Hospital",
        workplace_name: str = "",
        language: str = "English",
    ) -> DoctorContext:
        """Create and register a new doctor persona."""
        exp_map = {
            "student": ExperienceLevel.STUDENT,
            "resident": ExperienceLevel.RESIDENT,
            "attending": ExperienceLevel.ATTENDING,
            "senior": ExperienceLevel.SENIOR,
        }
        exp = exp_map.get(experience_level.lower(), ExperienceLevel.ATTENDING)
        doc_id = f"custom_{name.lower().replace(' ', '_').replace('.', '')}_{len(self.doctors)}"

        doctor = DoctorContext(
            id=doc_id,
            name=name,
            specialty=specialty,
            experience_level=exp,
            country=country,
            workplace_type=workplace_type,
            workplace_name=workplace_name or f"{specialty} Department",
            language=language,
        )
        self.doctors[doc_id] = doctor
        return doctor

    def create_patient_from_ehr(self, ehr_text: str, patient_id: Optional[str] = None) -> PatientEHR:
        """Parse unstructured EHR text with MedGemma into a structured patient."""
        prompt = (
            "Parse this clinical note into structured JSON.\n\n"
            f"CLINICAL NOTE:\n{ehr_text[:2000]}\n\n"
            "Return ONLY valid JSON with keys: name, age, sex, weight_kg, height_cm, "
            "chief_complaint, allergies, current_medications, medical_history, "
            "recent_labs, recent_vitals, hpi.\n\nJSON:"
        )

        response = self.medgemma.generate(prompt, max_tokens=1000, stream=False)

        parsed: Dict[str, Any] = {}
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                parsed = json.loads(response[start:end])
        except Exception:
            pass

        if not patient_id:
            patient_id = f"CUSTOM_{len(self.patients) + 1:03d}"

        weight = parsed.get("weight_kg", 70.0)
        height = parsed.get("height_cm", 170.0)
        bmi = round(weight / ((height / 100) ** 2), 1) if height > 0 else 24.2

        patient = PatientEHR(
            patient_id=patient_id,
            name=parsed.get("name", "Unknown Patient"),
            age=parsed.get("age", 0),
            sex=parsed.get("sex", "Unknown"),
            weight_kg=weight,
            height_cm=height,
            bmi=bmi,
            country=parsed.get("country", "USA"),
            insurance=parsed.get("insurance", "Unknown"),
            allergies=parsed.get("allergies", []),
            current_medications=[
                Medication(**m) if isinstance(m, dict) else Medication(name=str(m))
                for m in parsed.get("current_medications", [])
            ],
            medical_history=[
                MedicalCondition(
                    condition=h.get("condition", str(h)) if isinstance(h, dict) else str(h),
                    status=h.get("status", "active") if isinstance(h, dict) else "active",
                )
                for h in parsed.get("medical_history", [])
            ],
            chief_complaint=parsed.get("chief_complaint", ehr_text[:100]),
            hpi=parsed.get("hpi", ehr_text[:500]),
        )

        self.patients[patient_id] = patient
        return patient

    def create_patient_from_form(
        self,
        name: str,
        age: int,
        sex: str,
        chief_complaint: str,
        allergies: Optional[List[str]] = None,
        medications: Optional[List[Dict]] = None,
        medical_history: Optional[List[str]] = None,
        hpi: str = "",
        weight_kg: float = 70.0,
        height_cm: float = 170.0,
    ) -> PatientEHR:
        """Create a patient from structured form input."""
        patient_id = f"CUSTOM_{len(self.patients) + 1:03d}"
        bmi = round(weight_kg / ((height_cm / 100) ** 2), 1)

        patient = PatientEHR(
            patient_id=patient_id,
            name=name,
            age=age,
            sex=sex,
            weight_kg=weight_kg,
            height_cm=height_cm,
            bmi=bmi,
            allergies=allergies or [],
            current_medications=[
                Medication(**m) if isinstance(m, dict) else Medication(name=str(m))
                for m in (medications or [])
            ],
            medical_history=[
                MedicalCondition(condition=c, status="active")
                for c in (medical_history or [])
            ],
            chief_complaint=chief_complaint,
            hpi=hpi,
        )

        self.patients[patient_id] = patient
        return patient

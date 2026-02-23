"""
Pydantic models for ContextMed.

Defines the core data structures for doctors, patients, clinical responses,
and the LangGraph agent state.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ExperienceLevel(str, Enum):
    STUDENT = "student"
    RESIDENT = "resident"
    ATTENDING = "attending"
    SENIOR = "senior"


class QueryMode(str, Enum):
    REGULAR = "regular"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Doctor
# ---------------------------------------------------------------------------

class DoctorContext(BaseModel):
    id: str
    name: str
    specialty: str
    experience_level: ExperienceLevel
    country: str
    workplace_type: str
    workplace_name: str
    language: str = "English"
    preferences: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Patient EHR
# ---------------------------------------------------------------------------

class LabResult(BaseModel):
    value: Any
    unit: str = ""
    reference: str = ""
    flag: str = "N"  # N=normal, H=high, L=low


class Medication(BaseModel):
    name: str
    dose: str = ""
    frequency: str = ""
    indication: str = ""


class MedicalCondition(BaseModel):
    condition: str
    diagnosed_year: int = 0
    status: str = "active"


class ImagingResult(BaseModel):
    type: str
    date: str = ""
    findings: str = ""


class PatientEHR(BaseModel):
    patient_id: str
    name: str
    age: int
    sex: str
    weight_kg: float = 70.0
    height_cm: float = 170.0
    bmi: float = 24.2
    country: str = "USA"
    insurance: str = "Unknown"
    allergies: List[str] = Field(default_factory=list)
    current_medications: List[Medication] = Field(default_factory=list)
    medical_history: List[MedicalCondition] = Field(default_factory=list)
    surgical_history: List[str] = Field(default_factory=list)
    family_history: List[str] = Field(default_factory=list)
    social_history: Dict[str, Any] = Field(default_factory=dict)
    recent_labs: Dict[str, LabResult] = Field(default_factory=dict)
    recent_vitals: Dict[str, str] = Field(default_factory=dict)
    recent_imaging: List[ImagingResult] = Field(default_factory=list)
    chief_complaint: str = ""
    hpi: str = ""
    ros: Dict[str, List[str]] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Structured Clinical Response
# ---------------------------------------------------------------------------

class AllergyAlert(BaseModel):
    drug: str
    allergy: str
    severity: str = "high"


class Citation(BaseModel):
    title: str
    url: str
    source: str = ""


class ClinicalResponse(BaseModel):
    """Structured output returned by the agent."""
    assessment: str = ""
    differentials: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    safety_alerts: List[AllergyAlert] = Field(default_factory=list)
    followup: str = ""
    reasoning_trace: List[str] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    raw_response: str = ""


# ---------------------------------------------------------------------------
# API Request / Response Models
# ---------------------------------------------------------------------------

class ConversationMessage(BaseModel):
    role: str
    content: str


class QueryRequest(BaseModel):
    query: str
    doctor_id: str
    patient_id: Optional[str] = None
    mode: QueryMode = QueryMode.REGULAR
    conversation_history: List[ConversationMessage] = Field(default_factory=list)


class CreateDoctorRequest(BaseModel):
    name: str
    specialty: str
    experience_level: str
    country: str = "USA"
    workplace_type: str = "Hospital"
    workplace_name: str = ""
    language: str = "English"


class CreatePatientFromEHRRequest(BaseModel):
    ehr_text: str
    patient_id: Optional[str] = None


class CreatePatientFromFormRequest(BaseModel):
    name: str
    age: int
    sex: str
    chief_complaint: str
    allergies: List[str] = Field(default_factory=list)
    medications: List[Dict[str, str]] = Field(default_factory=list)
    medical_history: List[str] = Field(default_factory=list)
    hpi: str = ""
    weight_kg: float = 70.0
    height_cm: float = 170.0
    labs: Dict[str, Any] = Field(default_factory=dict)
    vitals: Dict[str, str] = Field(default_factory=dict)

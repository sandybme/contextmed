"""
Sample doctor personas and patient EHR data.

Covers USA and Germany to demonstrate geography-aware context switching.
"""

from __future__ import annotations

from contextmed.models import (
    DoctorContext,
    ExperienceLevel,
    ImagingResult,
    LabResult,
    MedicalCondition,
    Medication,
    PatientEHR,
)


# ===================================================================
# Doctor Personas
# ===================================================================

DOCTOR_PERSONAS = {
    # ---- USA ----
    "usa_er_attending": DoctorContext(
        id="usa_er_attending",
        name="Dr. Sarah Chen",
        specialty="Emergency Medicine",
        experience_level=ExperienceLevel.ATTENDING,
        country="USA",
        workplace_type="Urban Academic Hospital",
        workplace_name="Massachusetts General Hospital",
        preferences={"response_style": "concise", "wants_disposition": True},
    ),
    "usa_fm_resident": DoctorContext(
        id="usa_fm_resident",
        name="Dr. Michael Torres",
        specialty="Family Medicine",
        experience_level=ExperienceLevel.RESIDENT,
        country="USA",
        workplace_type="Rural Community Clinic",
        workplace_name="Riverside Family Health Center",
        preferences={"response_style": "educational", "limited_resources": True},
    ),
    "usa_med_student": DoctorContext(
        id="usa_med_student",
        name="James Wilson (MS3)",
        specialty="Internal Medicine (Rotation)",
        experience_level=ExperienceLevel.STUDENT,
        country="USA",
        workplace_type="Teaching Hospital",
        workplace_name="Johns Hopkins Hospital",
        preferences={"response_style": "detailed_educational", "needs_pathophysiology": True},
    ),
    # ---- Germany ----
    "de_internist": DoctorContext(
        id="de_internist",
        name="Dr. Hans Muller",
        specialty="Innere Medizin",
        experience_level=ExperienceLevel.ATTENDING,
        country="Germany",
        workplace_type="University Hospital",
        workplace_name="Charite - Universitatsmedizin Berlin",
        language="German",
        preferences={"response_style": "concise", "uses_european_guidelines": True},
    ),
    "de_hausarzt": DoctorContext(
        id="de_hausarzt",
        name="Dr. Anna Schmidt",
        specialty="Allgemeinmedizin",
        experience_level=ExperienceLevel.SENIOR,
        country="Germany",
        workplace_type="General Practice",
        workplace_name="Praxis Dr. Schmidt, Munchen",
        language="German",
        preferences={"response_style": "practical", "outpatient_focus": True},
    ),
    "de_pj_student": DoctorContext(
        id="de_pj_student",
        name="Lisa Weber (PJ)",
        specialty="Innere Medizin (PJ Tertial)",
        experience_level=ExperienceLevel.STUDENT,
        country="Germany",
        workplace_type="Teaching Hospital",
        workplace_name="Universitatsklinikum Heidelberg",
        language="German",
        preferences={"response_style": "detailed_educational", "learning_mode": True},
    ),
}


# ===================================================================
# Patient EHR Data — USA
# ===================================================================

USA_PATIENTS = {
    "USA_P001": PatientEHR(
        patient_id="USA_P001",
        name="Robert Johnson",
        age=67,
        sex="Male",
        weight_kg=92.5,
        height_cm=178,
        bmi=29.2,
        country="USA",
        insurance="Medicare",
        allergies=["Penicillin (rash)", "Sulfa (anaphylaxis)", "Shellfish"],
        current_medications=[
            Medication(name="Metformin", dose="1000mg", frequency="BID", indication="T2DM"),
            Medication(name="Lisinopril", dose="20mg", frequency="daily", indication="HTN"),
            Medication(name="Atorvastatin", dose="40mg", frequency="daily", indication="HLD"),
            Medication(name="Aspirin", dose="81mg", frequency="daily", indication="CAD prevention"),
            Medication(name="Metoprolol succinate", dose="50mg", frequency="daily", indication="HTN/CAD"),
        ],
        medical_history=[
            MedicalCondition(condition="Type 2 Diabetes Mellitus", diagnosed_year=2015, status="controlled"),
            MedicalCondition(condition="Hypertension", diagnosed_year=2010, status="controlled"),
            MedicalCondition(condition="Hyperlipidemia", diagnosed_year=2012, status="on treatment"),
            MedicalCondition(condition="Coronary Artery Disease", diagnosed_year=2020, status="s/p PCI to LAD"),
            MedicalCondition(condition="CKD Stage 3a", diagnosed_year=2022, status="stable"),
        ],
        surgical_history=["PCI with DES to LAD (2020)", "Appendectomy (1985)"],
        family_history=["Father: MI at 58", "Mother: T2DM, HTN", "Brother: T2DM"],
        social_history={
            "smoking": "Former, quit 2020, 30 pack-years",
            "alcohol": "Occasional, 2-3 drinks/week",
            "occupation": "Retired accountant",
        },
        recent_labs={
            "HbA1c": LabResult(value=7.8, unit="%", reference="<7.0", flag="H"),
            "Creatinine": LabResult(value=1.4, unit="mg/dL", reference="0.7-1.3", flag="H"),
            "eGFR": LabResult(value=52, unit="mL/min", reference=">60", flag="L"),
            "Potassium": LabResult(value=5.1, unit="mEq/L", reference="3.5-5.0", flag="H"),
            "NT-proBNP": LabResult(value=450, unit="pg/mL", reference="<300", flag="H"),
            "Hemoglobin": LabResult(value=12.8, unit="g/dL", reference="13.5-17.5", flag="L"),
            "LDL": LabResult(value=95, unit="mg/dL", reference="<70 (CAD)", flag="H"),
        },
        recent_vitals={
            "BP": "148/92 mmHg",
            "HR": "78 bpm, regular",
            "RR": "16/min",
            "SpO2": "96% on RA",
            "Temp": "98.4F",
        },
        recent_imaging=[
            ImagingResult(type="Echo", date="2025-11-15", findings="EF 45%, mild LVH, grade 1 diastolic dysfunction"),
            ImagingResult(type="CXR", date="2025-12-20", findings="Mild cardiomegaly, no acute infiltrates"),
        ],
        chief_complaint="Increasing shortness of breath and leg swelling for 2 weeks",
        hpi=(
            "67M with T2DM, HTN, CAD s/p PCI presents with 2 weeks of progressive "
            "dyspnea on exertion and bilateral LE edema. Previously walked 4 blocks, "
            "now SOB after 1 block. New 2-pillow orthopnea and occasional PND. "
            "Gained 7 lbs in 2 weeks. Ran out of Metoprolol for 5 days last week."
        ),
        ros={
            "constitutional": ["fatigue", "weight gain"],
            "cardiovascular": ["dyspnea on exertion", "orthopnea", "PND", "leg swelling"],
            "respiratory": ["dyspnea", "no cough"],
        },
    ),
    "USA_P002": PatientEHR(
        patient_id="USA_P002",
        name="Maria Santos",
        age=34,
        sex="Female",
        weight_kg=68.0,
        height_cm=163,
        bmi=25.6,
        country="USA",
        insurance="Blue Cross PPO",
        allergies=["Ibuprofen (GI upset)", "Latex"],
        current_medications=[
            Medication(name="Levothyroxine", dose="75mcg", frequency="daily", indication="Hypothyroidism"),
            Medication(name="Sertraline", dose="100mg", frequency="daily", indication="Anxiety"),
            Medication(name="Vitamin D", dose="2000 IU", frequency="daily", indication="Deficiency"),
        ],
        medical_history=[
            MedicalCondition(condition="Hashimoto's Thyroiditis", diagnosed_year=2018, status="on replacement"),
            MedicalCondition(condition="Generalized Anxiety Disorder", diagnosed_year=2019, status="controlled"),
            MedicalCondition(condition="Migraine without aura", diagnosed_year=2015, status="intermittent"),
        ],
        surgical_history=["Laparoscopic cholecystectomy (2021)"],
        family_history=["Mother: Hypothyroidism, Breast cancer at 52", "Sister: SLE"],
        social_history={"smoking": "Never", "alcohol": "Social", "occupation": "Software engineer"},
        recent_labs={
            "TSH": LabResult(value=2.4, unit="mIU/L", reference="0.4-4.0", flag="N"),
            "ANA": LabResult(value="1:80", unit="titer", reference="<1:40", flag="H"),
            "ESR": LabResult(value=28, unit="mm/hr", reference="0-20", flag="H"),
            "CRP": LabResult(value=1.2, unit="mg/dL", reference="<0.5", flag="H"),
            "Hemoglobin": LabResult(value=12.1, unit="g/dL", reference="12.0-16.0", flag="N"),
        },
        recent_vitals={"BP": "118/72 mmHg", "HR": "76 bpm", "Temp": "99.1F", "SpO2": "99%"},
        chief_complaint="Joint pain and fatigue for 6 weeks",
        hpi=(
            "34F with Hashimoto's presents with 6 weeks of joint pain (hands, wrists, knees) "
            "and fatigue. Morning stiffness ~1 hour. Low-grade fevers. New photosensitivity "
            "and faint malar rash. Sister recently diagnosed with lupus."
        ),
        ros={
            "constitutional": ["fatigue", "low-grade fevers"],
            "skin": ["photosensitivity", "malar rash"],
            "msk": ["polyarthralgias", "morning stiffness"],
        },
    ),
}


# ===================================================================
# Patient EHR Data — Germany
# ===================================================================

GERMANY_PATIENTS = {
    "DE_P001": PatientEHR(
        patient_id="DE_P001",
        name="Klaus Becker",
        age=72,
        sex="Male",
        weight_kg=85.0,
        height_cm=175,
        bmi=27.8,
        country="Germany",
        insurance="AOK Bayern",
        allergies=["Amoxicillin (Exanthem)", "Kontrastmittel (Anaphylaxie)"],
        current_medications=[
            Medication(name="Ramipril", dose="5mg", frequency="taglich", indication="Hypertonie"),
            Medication(name="Bisoprolol", dose="5mg", frequency="taglich", indication="KHK/VHF"),
            Medication(name="ASS", dose="100mg", frequency="taglich", indication="KHK"),
            Medication(name="Simvastatin", dose="40mg", frequency="abends", indication="Hyperlipidamie"),
            Medication(name="Pantoprazol", dose="20mg", frequency="taglich", indication="Reflux"),
        ],
        medical_history=[
            MedicalCondition(condition="KHK (Koronare Herzkrankheit)", diagnosed_year=2018, status="Z.n. PTCA LAD"),
            MedicalCondition(condition="Arterielle Hypertonie", diagnosed_year=2008, status="eingestellt"),
            MedicalCondition(condition="Vorhofflimmern paroxysmal", diagnosed_year=2022, status="Frequenzkontrolle"),
            MedicalCondition(condition="COPD GOLD II", diagnosed_year=2019, status="stabil"),
        ],
        surgical_history=["PTCA mit DES LAD (2018)", "Appendektomie (1965)"],
        family_history=["Vater: Herzinfarkt mit 65", "Mutter: Schlaganfall"],
        social_history={"smoking": "Ex-Raucher seit 2018, 40 Packungsjahre", "alcohol": "Gelegentlich Bier"},
        recent_labs={
            "Kreatinin": LabResult(value=1.3, unit="mg/dL", reference="0.7-1.2", flag="H"),
            "eGFR": LabResult(value=55, unit="mL/min", reference=">60", flag="L"),
            "NT-proBNP": LabResult(value=890, unit="pg/mL", reference="<300", flag="H"),
            "Kalium": LabResult(value=4.8, unit="mmol/L", reference="3.5-5.0", flag="N"),
            "Hamoglobin": LabResult(value=13.2, unit="g/dL", reference="13.5-17.5", flag="L"),
        },
        recent_vitals={"BP": "152/88 mmHg", "HR": "88/min, unregelmassig", "SpO2": "94%", "Temp": "36.8C"},
        recent_imaging=[
            ImagingResult(type="Echo", date="2025-10-10", findings="EF 40%, LA dilatiert, diastolische Dysfunktion Grad II"),
        ],
        chief_complaint="Zunehmende Belastungsdyspnoe und Beinodeme seit 10 Tagen",
        hpi=(
            "72-jahriger Patient mit KHK, Hypertonie, paroxysmalem VHF. "
            "Seit 10 Tagen zunehmende Belastungsdyspnoe (fruher 500m, jetzt 100m). "
            "Unterschenkelodeme beidseits, 2-Kissen-Orthopnoe (neu). "
            "Gelegentliches Herzstolpern."
        ),
        ros={
            "konstitutionell": ["Mudigkeit", "Gewichtszunahme 3kg"],
            "kardiovaskular": ["Belastungsdyspnoe", "Orthopnoe", "Beinodeme", "Palpitationen"],
        },
    ),
    "DE_P002": PatientEHR(
        patient_id="DE_P002",
        name="Sabine Hoffmann",
        age=45,
        sex="Female",
        weight_kg=72.0,
        height_cm=168,
        bmi=25.5,
        country="Germany",
        insurance="TK",
        allergies=["Metamizol", "Nickel"],
        current_medications=[
            Medication(name="L-Thyroxin", dose="100ug", frequency="taglich nuchtern", indication="Hypothyreose"),
            Medication(name="Citalopram", dose="20mg", frequency="taglich", indication="Depression"),
        ],
        medical_history=[
            MedicalCondition(condition="Hashimoto-Thyreoiditis", diagnosed_year=2016, status="substituiert"),
            MedicalCondition(condition="Rezidivierende depressive Storung", diagnosed_year=2018, status="unter Therapie"),
            MedicalCondition(condition="Migrane ohne Aura", diagnosed_year=2008, status="intermittierend"),
        ],
        surgical_history=["Sectio caesarea (2012)"],
        family_history=["Mutter: Hashimoto, RA", "Schwester: MS"],
        social_history={"smoking": "Nie", "alcohol": "Selten", "occupation": "Lehrerin"},
        recent_labs={
            "TSH": LabResult(value=1.8, unit="mU/L", reference="0.4-4.0", flag="N"),
            "Hamoglobin": LabResult(value=11.8, unit="g/dL", reference="12.0-16.0", flag="L"),
            "Ferritin": LabResult(value=18, unit="ng/mL", reference="15-150", flag="N"),
            "Vitamin D": LabResult(value=22, unit="ng/mL", reference="30-100", flag="L"),
        },
        recent_vitals={"BP": "125/78 mmHg", "HR": "72/min", "SpO2": "98%", "Temp": "36.6C"},
        chief_complaint="Zunehmende Mudigkeit und Kopfschmerzen seit 4 Wochen",
        hpi=(
            "45-jahrige Patientin mit Hashimoto und Depression. "
            "Seit 4 Wochen Mudigkeit und dumpfe Kopfschmerzen (anders als Migrane). "
            "Konzentrationsstorungen, Schwindel beim Aufstehen. Stress bei Arbeit."
        ),
        ros={
            "konstitutionell": ["Mudigkeit"],
            "neurologisch": ["Kopfschmerzen", "Konzentrationsstorung", "Schwindel"],
        },
    ),
}


# Combined registry
ALL_PATIENTS = {**USA_PATIENTS, **GERMANY_PATIENTS}

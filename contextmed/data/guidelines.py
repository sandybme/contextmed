"""
Local clinical guidelines database for ContextMed.

Contains curated excerpts from major clinical guidelines, organized by:
- Country/Region (USA, Germany, EU)
- Condition/Topic
- Source organization

This enables geography-aware guideline retrieval without external API dependencies.
"""

from typing import Dict, List, Any

# ==============================================================================
# USA GUIDELINES (ACC/AHA, ADA, etc.)
# ==============================================================================

USA_GUIDELINES: List[Dict[str, Any]] = [
    # Heart Failure Guidelines
    {
        "id": "usa_hf_2022",
        "title": "2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure",
        "source": "American Heart Association / American College of Cardiology",
        "year": 2022,
        "country": "USA",
        "conditions": ["heart failure", "hfref", "hfpef", "cardiomyopathy"],
        "keywords": ["heart failure", "ejection fraction", "diuretics", "ace inhibitor", "arb", "arni", "beta blocker", "sglt2", "mra"],
        "url": "https://www.ahajournals.org/doi/10.1161/CIR.0000000000001063",
        "content": """
GUIDELINE-DIRECTED MEDICAL THERAPY (GDMT) FOR HFrEF:

1. FOUNDATIONAL THERAPY (Start all 4 pillars):
   - ACEi/ARB/ARNI: Sacubitril-valsartan preferred if tolerated (Class I)
   - Beta-blocker: Carvedilol, metoprolol succinate, or bisoprolol (Class I)
   - MRA: Spironolactone or eplerenone (Class I)
   - SGLT2i: Dapagliflozin or empagliflozin (Class I) - NEW in 2022

2. DIURETICS for volume management:
   - Loop diuretics (furosemide, bumetanide, torsemide) for congestion
   - Target euvolemia, not a specific dose

3. ADDITIONAL THERAPIES:
   - Hydralazine + nitrate for African Americans (Class I)
   - ICD if EF ≤35% after 3 months of GDMT
   - CRT if LBBB and QRS ≥150ms

4. MONITORING:
   - Renal function and potassium within 1-2 weeks of initiation
   - Target: BP, HR, symptoms, volume status

5. CONTRAINDICATIONS:
   - ACEi/ARB/ARNI: Avoid in hyperkalemia (K>5.5), severe renal impairment
   - Beta-blockers: Avoid in decompensated HF, severe bradycardia
   - MRA: Avoid if eGFR <30, K>5.0
""",
    },
    {
        "id": "usa_hf_acute_2022",
        "title": "2022 AHA/ACC Guideline - Acute Decompensated Heart Failure Management",
        "source": "American Heart Association",
        "year": 2022,
        "country": "USA",
        "conditions": ["acute heart failure", "adhf", "decompensated heart failure", "pulmonary edema"],
        "keywords": ["acute", "decompensated", "diuretic", "inotrope", "vasodilator", "congestion"],
        "url": "https://www.ahajournals.org/doi/10.1161/CIR.0000000000001063",
        "content": """
ACUTE DECOMPENSATED HEART FAILURE (ADHF):

INITIAL ASSESSMENT:
- Determine congestion (wet/dry) and perfusion (warm/cold)
- Identify precipitants: ischemia, arrhythmia, infection, non-adherence

TREATMENT BY PROFILE:

1. WARM AND WET (most common):
   - IV loop diuretics: Furosemide 40mg IV (or 1-2.5x home dose)
   - Consider doubling dose if inadequate response in 2 hours
   - Target urine output: 100-150 mL/hour initially
   - Add thiazide (metolazone 5mg) if diuretic resistance

2. COLD AND WET:
   - Inotropic support may be needed
   - Dobutamine 2-5 mcg/kg/min or milrinone
   - Vasodilators if BP allows (nitroprusside, nitroglycerin)

3. COLD AND DRY:
   - Cautious fluid challenge
   - Consider inotropic support

MONITORING:
- Daily weights, strict I/O
- BMP every 24-48 hours
- Continuous telemetry

DISCHARGE CRITERIA:
- Transition to oral diuretics with stable weight x24h
- Ambulatory SpO2 >90%
- Stable vital signs
- GDMT optimized or plan in place
""",
    },
    # Diabetes Guidelines
    {
        "id": "usa_dm_2024",
        "title": "ADA Standards of Care in Diabetes - 2024",
        "source": "American Diabetes Association",
        "year": 2024,
        "country": "USA",
        "conditions": ["diabetes", "type 2 diabetes", "t2dm", "hyperglycemia"],
        "keywords": ["diabetes", "a1c", "hba1c", "metformin", "sglt2", "glp1", "insulin", "glucose"],
        "url": "https://diabetesjournals.org/care/issue/47/Supplement_1",
        "content": """
ADA 2024 GLYCEMIC MANAGEMENT:

A1C TARGETS:
- General: <7% for most adults
- Less stringent (7.5-8%): elderly, limited life expectancy, hypoglycemia risk
- More stringent (<6.5%): newly diagnosed, long life expectancy if achievable without hypoglycemia

PHARMACOTHERAPY APPROACH:

1. FIRST-LINE: Metformin + lifestyle (unless contraindicated)
   - Start 500mg daily, titrate to 1000mg BID
   - Hold if eGFR <30, avoid if <20

2. SECOND-LINE (choose based on comorbidities):

   WITH ASCVD or HIGH CV RISK:
   - GLP-1 RA with proven CV benefit (semaglutide, liraglutide, dulaglutide)
   - OR SGLT2i (empagliflozin, canagliflozin, dapagliflozin)

   WITH HEART FAILURE:
   - SGLT2i preferred (Class I recommendation)

   WITH CKD:
   - SGLT2i if eGFR ≥20 (empagliflozin, dapagliflozin)
   - Finerenone for additional CV/kidney protection

   FOR WEIGHT MANAGEMENT:
   - GLP-1 RA (semaglutide has greatest weight loss)
   - Tirzepatide (GIP/GLP-1 RA)

3. INSULIN:
   - Add basal insulin if A1C remains above target
   - Start 10 units or 0.1-0.2 units/kg
   - Titrate by 2 units every 3 days to fasting glucose target

MONITORING:
- A1C every 3 months until at goal, then every 6 months
- Annual comprehensive metabolic panel
- Annual urine albumin/creatinine ratio
""",
    },
    # Hypertension
    {
        "id": "usa_htn_2017",
        "title": "2017 ACC/AHA Guideline for High Blood Pressure in Adults",
        "source": "American College of Cardiology / American Heart Association",
        "year": 2017,
        "country": "USA",
        "conditions": ["hypertension", "high blood pressure", "htn"],
        "keywords": ["blood pressure", "hypertension", "ace inhibitor", "arb", "ccb", "thiazide", "antihypertensive"],
        "url": "https://www.ahajournals.org/doi/10.1161/HYP.0000000000000065",
        "content": """
2017 ACC/AHA BLOOD PRESSURE GUIDELINES:

CLASSIFICATION:
- Normal: <120/<80 mmHg
- Elevated: 120-129/<80 mmHg
- Stage 1 HTN: 130-139 OR 80-89 mmHg
- Stage 2 HTN: ≥140 OR ≥90 mmHg
- Hypertensive Crisis: >180/>120 mmHg

BP TARGETS:
- General population with CVD or 10-yr risk ≥10%: <130/80
- General population without CVD: <130/80 recommended
- Older adults (≥65 years): <130 systolic if tolerated

FIRST-LINE MEDICATIONS:
1. Thiazide-type diuretics (chlorthalidone preferred)
2. ACE inhibitors or ARBs (not together)
3. Calcium channel blockers (amlodipine, nifedipine ER)

SPECIAL POPULATIONS:
- Black patients: CCB or thiazide first-line (ACEi less effective as monotherapy)
- CKD with albuminuria: ACEi or ARB
- Diabetes: ACEi or ARB preferred
- Heart failure: ACEi/ARB + beta-blocker + diuretic

COMBINATION THERAPY:
- Most patients need 2+ drugs
- Start with 2 drugs if BP ≥20/10 above goal
- Single-pill combinations improve adherence

FOLLOW-UP:
- Monthly until at goal
- Then every 3-6 months
""",
    },
    # Atrial Fibrillation
    {
        "id": "usa_afib_2023",
        "title": "2023 ACC/AHA/ACCP/HRS Guideline for Atrial Fibrillation",
        "source": "ACC/AHA/ACCP/HRS",
        "year": 2023,
        "country": "USA",
        "conditions": ["atrial fibrillation", "afib", "af", "arrhythmia"],
        "keywords": ["atrial fibrillation", "anticoagulation", "rate control", "rhythm control", "ablation", "doac", "warfarin"],
        "url": "https://www.ahajournals.org/doi/10.1161/CIR.0000000000001193",
        "content": """
2023 ACC/AHA ATRIAL FIBRILLATION GUIDELINES:

STROKE PREVENTION (CHA2DS2-VASc Score):
- Score 0 (men) or 1 (women): No anticoagulation
- Score 1 (men) or 2 (women): Consider anticoagulation
- Score ≥2 (men) or ≥3 (women): Anticoagulation recommended

ANTICOAGULATION CHOICE:
- DOACs preferred over warfarin (Class I)
  - Apixaban 5mg BID (2.5mg BID if 2 of: age ≥80, weight ≤60kg, Cr ≥1.5)
  - Rivaroxaban 20mg daily with food (15mg if CrCl 15-50)
  - Dabigatran 150mg BID (110mg BID if age >80 or increased bleeding risk)
  - Edoxaban 60mg daily (30mg if CrCl 15-50, weight ≤60kg)
- Warfarin: mechanical valve, moderate-severe mitral stenosis

RATE CONTROL:
- Target resting HR <110 bpm (lenient) or <80 bpm (strict)
- First-line: Beta-blockers or non-DHP CCB (diltiazem, verapamil)
- Digoxin: add-on for rate control, especially in HF
- Amiodarone: if others fail (not first-line)

RHYTHM CONTROL:
- Consider if symptomatic despite rate control
- Options: cardioversion, antiarrhythmics, ablation
- Antiarrhythmics:
  - No structural heart disease: flecainide, propafenone, sotalol
  - With structural disease: amiodarone, dofetilide
- Catheter ablation: Class I for symptomatic AFib after failed AAD

LEFT ATRIAL APPENDAGE:
- LAA occlusion (Watchman) if long-term anticoagulation contraindicated
""",
    },
]

# ==============================================================================
# GERMAN / EUROPEAN GUIDELINES (AWMF, ESC, DGK)
# ==============================================================================

GERMANY_GUIDELINES: List[Dict[str, Any]] = [
    # Heart Failure - ESC
    {
        "id": "esc_hf_2021",
        "title": "2021 ESC Guidelines for Heart Failure",
        "source": "European Society of Cardiology",
        "year": 2021,
        "country": "Germany",
        "conditions": ["heart failure", "herzinsuffizienz", "hfref", "hfpef"],
        "keywords": ["herzinsuffizienz", "heart failure", "ejektionsfraktion", "diuretika", "ace-hemmer", "betablocker", "sglt2"],
        "url": "https://www.escardio.org/Guidelines/Clinical-Practice-Guidelines/Heart-Failure",
        "content": """
ESC 2021 HERZINSUFFIZIENZ-LEITLINIE:

KLASSIFIKATION:
- HFrEF: LVEF ≤40%
- HFmrEF: LVEF 41-49%
- HFpEF: LVEF ≥50%

THERAPIE BEI HFrEF (alle 4 Säulen empfohlen):

1. ACE-HEMMER / ARNI:
   - Sacubitril/Valsartan bevorzugt bei tolerierter ACE-Hemmer-Therapie
   - Enalapril, Ramipril als Alternative
   - CAVE: Hyperkaliämie, Niereninsuffizienz

2. BETABLOCKER:
   - Bisoprolol, Carvedilol, Metoprolol-Succinat, Nebivolol
   - Zieldosis anstreben, langsam titrieren
   - Nicht bei dekompensierter HF beginnen

3. MRA (Mineralokortikoid-Rezeptor-Antagonisten):
   - Spironolacton oder Eplerenon
   - CAVE: Kalium >5.0 mmol/L, eGFR <30

4. SGLT2-INHIBITOREN (NEU - Klasse I):
   - Dapagliflozin oder Empagliflozin
   - Auch ohne Diabetes empfohlen
   - eGFR-Grenze beachten (≥20-25 ml/min)

DIURETIKA:
- Schleifendiuretika bei Kongestion (Furosemid, Torasemid)
- Keine Prognoseverbesserung, nur symptomatisch

DEVICE-THERAPIE:
- ICD: LVEF ≤35% trotz 3 Monate optimaler Therapie
- CRT: LVEF ≤35%, LBBB, QRS ≥150ms

MONITORING:
- Nierenfunktion und Elektrolyte 1-2 Wochen nach Dosisänderung
- NT-proBNP zur Verlaufskontrolle
""",
    },
    {
        "id": "esc_dm_2023",
        "title": "2023 ESC Guidelines for Cardiovascular Disease in Diabetes",
        "source": "European Society of Cardiology",
        "year": 2023,
        "country": "Germany",
        "conditions": ["diabetes", "typ 2 diabetes", "kardiovaskulär"],
        "keywords": ["diabetes", "hba1c", "metformin", "sglt2", "glp1", "kardiovaskulär", "risiko"],
        "url": "https://www.escardio.org/Guidelines/Clinical-Practice-Guidelines/Diabetes",
        "content": """
ESC 2023 DIABETES UND KARDIOVASKULÄRES RISIKO:

RISIKOSTRATIFIZIERUNG:
- Sehr hohes Risiko: manifeste ASCVD, Endorganschaden, ≥3 Risikofaktoren
- Hohes Risiko: Diabetes >10 Jahre, 1-2 Risikofaktoren
- Moderates Risiko: jung, kurze Diabetesdauer, keine Risikofaktoren

GLYKÄMISCHE ZIELE:
- HbA1c <7% für die meisten
- <6.5% wenn sicher erreichbar (kurze Dauer, keine Hypoglykämien)
- <8% bei Älteren, begrenzter Lebenserwartung

THERAPIEALGORITHMUS:

1. MIT ATHEROSKLEROTISCHER ERKRANKUNG:
   - GLP-1 RA mit nachgewiesenem CV-Benefit ODER
   - SGLT2-Inhibitor
   - Unabhängig von HbA1c-Ausgangswert

2. MIT HERZINSUFFIZIENZ:
   - SGLT2-Inhibitor (Klasse I) - oberste Priorität
   - Dapagliflozin oder Empagliflozin

3. MIT CHRONISCHER NIERENERKRANKUNG:
   - SGLT2-Inhibitor wenn eGFR ≥20
   - Finerenon zusätzlich für CV/renale Protektion

4. OHNE KARDIOVASKULÄRE ERKRANKUNG:
   - Metformin als Basistherapie
   - Weitere Therapie nach individuellen Faktoren

BLUTDRUCKZIELE:
- Systolisch 120-130 mmHg wenn toleriert
- <140/80 mmHg als Mindestziel

LIPIDE:
- LDL <55 mg/dL bei sehr hohem Risiko
- LDL <70 mg/dL bei hohem Risiko
""",
    },
    # AWMF Guideline
    {
        "id": "awmf_copd_2020",
        "title": "AWMF S2k-Leitlinie COPD",
        "source": "AWMF / Deutsche Gesellschaft für Pneumologie",
        "year": 2020,
        "country": "Germany",
        "conditions": ["copd", "chronisch obstruktive lungenerkrankung", "lungenemphysem"],
        "keywords": ["copd", "lunge", "bronchodilatator", "inhalation", "exazerbation", "sauerstoff"],
        "url": "https://www.awmf.org/leitlinien/detail/ll/020-006.html",
        "content": """
AWMF COPD-LEITLINIE:

DIAGNOSTIK:
- Spirometrie: FEV1/FVC <0.7 nach Bronchodilatation
- GOLD-Stadien nach FEV1:
  - GOLD 1: ≥80% (leicht)
  - GOLD 2: 50-79% (mittel)
  - GOLD 3: 30-49% (schwer)
  - GOLD 4: <30% (sehr schwer)

ABCD-KLASSIFIKATION (Symptome + Exazerbationen):
- Gruppe A: wenig Symptome, wenig Exazerbationen
- Gruppe B: viel Symptome, wenig Exazerbationen
- Gruppe E: ≥2 Exazerbationen oder ≥1 mit Hospitalisierung

PHARMAKOTHERAPIE:

1. GRUPPE A:
   - Bronchodilatator bei Bedarf (SABA oder SAMA)

2. GRUPPE B:
   - LABA oder LAMA als Dauertherapie
   - Bei persistierenden Symptomen: LABA + LAMA

3. GRUPPE E:
   - LABA + LAMA als Basis
   - Bei Eosinophilen ≥300: + ICS (Triple-Therapie)
   - Bei Eosinophilen <100: LABA + LAMA ohne ICS

EXAZERBATIONSMANAGEMENT:
- Systemische Kortikosteroide: Prednisolon 40mg/Tag für 5 Tage
- Antibiotika bei eitriger Sputum oder schwerer Exazerbation
- Sauerstoff: Ziel SpO2 88-92%

NICHT-MEDIKAMENTÖS:
- Raucherentwöhnung (wichtigste Maßnahme!)
- Pneumologische Rehabilitation
- Impfungen: Influenza, Pneumokokken, COVID-19
""",
    },
    # Hypertension ESC
    {
        "id": "esc_htn_2023",
        "title": "2023 ESC Guidelines for Arterial Hypertension",
        "source": "European Society of Cardiology / European Society of Hypertension",
        "year": 2023,
        "country": "Germany",
        "conditions": ["hypertonie", "bluthochdruck", "arterielle hypertonie"],
        "keywords": ["hypertonie", "blutdruck", "antihypertensiva", "ace-hemmer", "betablocker", "calcium"],
        "url": "https://www.escardio.org/Guidelines/Clinical-Practice-Guidelines/Arterial-Hypertension",
        "content": """
ESC 2023 ARTERIELLE HYPERTONIE:

DEFINITION:
- Praxisblutdruck ≥140/90 mmHg
- Ambulant (24h): ≥130/80 mmHg
- Heimblutdruck: ≥135/85 mmHg

ZIELWERTE:
- Allgemein: <130/80 mmHg wenn toleriert
- Ältere (>65 Jahre): Systolisch 130-139 mmHg
- Niemals <120/70 mmHg

MEDIKAMENTÖSE THERAPIE:

ERSTLINIENTHERAPIE (Monotherapie selten ausreichend):
- ACE-Hemmer ODER Angiotensin-Rezeptorblocker (ARB)
- Calciumkanalblocker (Amlodipin)
- Thiazid-ähnliche Diuretika (Chlortalidon, Indapamid)

STANDARDKOMBINATIONEN:
1. ACE-Hemmer/ARB + Calciumkanalblocker
2. ACE-Hemmer/ARB + Diuretikum
3. Triple: ACE-Hemmer/ARB + CCB + Diuretikum

SPEZIELLE SITUATIONEN:
- KHK/Herzinsuffizienz: Betablocker, ACE-Hemmer
- Diabetes mit Proteinurie: ACE-Hemmer/ARB
- Schwangerschaft: Methyldopa, Labetalol, Nifedipin

RESISTENTE HYPERTONIE:
- Definition: >140/90 trotz 3 Medikamente inkl. Diuretikum
- Hinzufügen: Spironolacton 25-50mg

HYPERTENSIVER NOTFALL:
- Blutdruck >180/120 mit Endorganschaden
- Ziel: 25% Reduktion in ersten Stunden
- i.v. Urapidil, Nitrate, Clonidin
""",
    },
    # Atrial Fibrillation ESC
    {
        "id": "esc_afib_2020",
        "title": "2020 ESC Guidelines for Atrial Fibrillation",
        "source": "European Society of Cardiology",
        "year": 2020,
        "country": "Germany",
        "conditions": ["vorhofflimmern", "atrial fibrillation", "vhf"],
        "keywords": ["vorhofflimmern", "antikoagulation", "frequenzkontrolle", "rhythmuskontrolle", "ablation"],
        "url": "https://www.escardio.org/Guidelines/Clinical-Practice-Guidelines/Atrial-Fibrillation",
        "content": """
ESC 2020 VORHOFFLIMMERN-LEITLINIE:

CC ZU ABC - INTEGRIERTES MANAGEMENT:

A - ANTIKOAGULATION:
CHA2DS2-VASc Score:
- Männer ≥2, Frauen ≥3: Antikoagulation empfohlen (Klasse I)
- Männer =1, Frauen =2: Antikoagulation erwägen (Klasse IIa)

ANTIKOAGULANZIEN:
- NOAK bevorzugt gegenüber VKA (außer: mechanische Klappe, mittelschwere-schwere Mitralstenose)
- Apixaban 5mg 2x täglich
- Rivaroxaban 20mg 1x täglich mit Essen
- Dabigatran 150mg 2x täglich
- Edoxaban 60mg 1x täglich

Dosisreduktion bei:
- Niereninsuffizienz (CrCl beachten)
- Alter >80 Jahre (bei einigen NOAKs)
- Gewicht <60kg
- Interaktionen

B - BESSERE SYMPTOMKONTROLLE:

FREQUENZKONTROLLE:
- Ziel-HF: <110/min (lenient) oder <80/min (strikt)
- Betablocker oder Diltiazem/Verapamil
- Digitalis bei Herzinsuffizienz als Add-on

RHYTHMUSKONTROLLE:
- Bei symptomatischen Patienten
- Frühe Rhythmuskontrolle vorteilhaft (EAST-AFNET 4)
- Optionen: Kardioversion, Antiarrhythmika, Ablation

Antiarrhythmika:
- Ohne strukturelle Herzerkrankung: Flecainid, Propafenon
- Mit struktureller Erkrankung: Amiodaron

Katheterablation:
- Klasse I bei symptomatischem paroxysmalem VHF nach AAD-Versagen
- Klasse IIa als First-Line bei ausgewählten Patienten

C - KARDIOVASKULÄRE RISIKOFAKTOREN:
- Hypertonie behandeln
- Gewichtsreduktion
- Schlafapnoe behandeln
- Alkoholreduktion
""",
    },
]


# ==============================================================================
# Combined Guidelines Database
# ==============================================================================

ALL_GUIDELINES: List[Dict[str, Any]] = USA_GUIDELINES + GERMANY_GUIDELINES


def get_guidelines_by_country(country: str) -> List[Dict[str, Any]]:
    """Get all guidelines for a specific country."""
    country_map = {
        "USA": USA_GUIDELINES,
        "Germany": GERMANY_GUIDELINES,
        "Deutschland": GERMANY_GUIDELINES,
        "EU": GERMANY_GUIDELINES,  # Use ESC guidelines for EU
        "Europe": GERMANY_GUIDELINES,
    }
    return country_map.get(country, USA_GUIDELINES)


def search_local_guidelines(
    query: str,
    country: str = "USA",
    max_results: int = 3,
) -> List[Dict[str, str]]:
    """
    Search local guidelines database using keyword matching.

    Args:
        query: Search query
        country: Country for guideline filtering
        max_results: Maximum number of results

    Returns:
        List of matching guidelines with title, url, content
    """
    query_lower = query.lower()
    query_terms = query_lower.split()

    # Get guidelines for this country
    guidelines = get_guidelines_by_country(country)

    # Score each guideline based on relevance
    scored_results = []
    for g in guidelines:
        score = 0

        # Check conditions match
        for condition in g.get("conditions", []):
            if condition.lower() in query_lower:
                score += 10
            for term in query_terms:
                if term in condition.lower():
                    score += 3

        # Check keywords match
        for keyword in g.get("keywords", []):
            if keyword.lower() in query_lower:
                score += 5
            for term in query_terms:
                if term in keyword.lower():
                    score += 2

        # Check title match
        title_lower = g.get("title", "").lower()
        for term in query_terms:
            if term in title_lower:
                score += 4

        # Check content match
        content_lower = g.get("content", "").lower()
        for term in query_terms:
            if term in content_lower:
                score += 1

        if score > 0:
            scored_results.append((score, g))

    # Sort by score descending
    scored_results.sort(key=lambda x: x[0], reverse=True)

    # Return top results
    results = []
    for score, g in scored_results[:max_results]:
        results.append({
            "title": f"{g['title']} ({g['source']}, {g['year']})",
            "url": g.get("url", ""),
            "content": g.get("content", "")[:500],
            "source": g.get("source", ""),
            "year": g.get("year", ""),
        })

    return results

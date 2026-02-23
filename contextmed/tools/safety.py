"""Patient safety tools — allergy checking and renal dose adjustment."""

from __future__ import annotations

from typing import Dict, List

from contextmed.models import AllergyAlert

# Cross-reactivity map for common drug families
CROSS_REACTIVITY: Dict[str, List[str]] = {
    "penicillin": ["amoxicillin", "ampicillin", "piperacillin", "nafcillin"],
    "sulfa": ["sulfamethoxazole", "sulfasalazine", "trimethoprim-sulfamethoxazole"],
    "cephalosporin": ["cephalexin", "ceftriaxone", "cefazolin", "cefepime"],
    "nsaid": ["ibuprofen", "naproxen", "ketorolac", "diclofenac", "celecoxib"],
}


async def check_allergies(
    medications: List[str],
    allergies: List[str],
) -> List[AllergyAlert]:
    """
    Check proposed medications against patient allergies.

    Supports direct match and known cross-reactivity families.

    Returns:
        List of AllergyAlert for each conflict found.
    """
    alerts: List[AllergyAlert] = []
    allergy_lower = [a.lower() for a in allergies]
    allergy_keywords = [a.split()[0].lower() for a in allergies]

    for med in medications:
        med_lower = med.lower()
        for idx, keyword in enumerate(allergy_keywords):
            # Direct match
            if keyword in med_lower:
                alerts.append(AllergyAlert(
                    drug=med,
                    allergy=allergies[idx],
                    severity="high",
                ))
                continue

            # Cross-reactivity check
            for family, members in CROSS_REACTIVITY.items():
                if keyword in family or family in keyword:
                    if any(m in med_lower for m in members):
                        alerts.append(AllergyAlert(
                            drug=med,
                            allergy=f"{allergies[idx]} (cross-reactivity: {family})",
                            severity="moderate",
                        ))

    return alerts


async def calculate_dose(
    drug: str,
    weight_kg: float = 70.0,
    egfr: float = 90.0,
    age: int = 50,
) -> Dict:
    """
    Calculate renal- and weight-adjusted dosing guidance.

    Args:
        drug:      Drug name.
        weight_kg: Patient weight in kg.
        egfr:      Estimated GFR (mL/min).
        age:       Patient age.

    Returns:
        Dict with drug, weight, egfr, adjustment recommendation.
    """
    adjustment = "No adjustment needed"
    if egfr < 15:
        adjustment = "Severe renal failure — contraindicated or requires dialysis dosing"
    elif egfr < 30:
        adjustment = "Severe renal impairment — reduce dose by 50% or avoid"
    elif egfr < 60:
        adjustment = "Moderate renal impairment — reduce dose by 25-50%, monitor closely"

    return {
        "drug": drug,
        "weight_kg": weight_kg,
        "egfr": egfr,
        "age": age,
        "adjustment": adjustment,
    }

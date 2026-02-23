"""OpenFDA drug label search (free, no API key needed)."""

from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

import aiohttp


async def _fetch_drug(
    session: aiohttp.ClientSession,
    drug_name: str,
) -> Optional[Dict]:
    """Fetch a single drug's FDA label information."""
    name = drug_name.split()[0].lower()
    url = (
        "https://api.fda.gov/drug/label.json"
        f"?search=openfda.generic_name:{name}&limit=1"
    )
    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            results = data.get("results")
            if not results:
                return None
            r = results[0]
            return {
                "drug": name,
                "warnings": (r.get("warnings") or [""])[:1],
                "contraindications": (r.get("contraindications") or [""])[:1],
                "drug_interactions": (r.get("drug_interactions") or [""])[:1],
            }
    except Exception:
        return None


async def search_openfda(
    drug_names: List[str],
    timeout_seconds: int = 10,
) -> List[Dict]:
    """
    Search OpenFDA for drug safety information.

    Args:
        drug_names:      List of drug names to look up.
        timeout_seconds: HTTP request timeout.

    Returns:
        List of dicts with drug, warnings, contraindications, drug_interactions.
    """
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [_fetch_drug(session, d) for d in drug_names[:5]]
        fetched = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in fetched if isinstance(r, dict)]

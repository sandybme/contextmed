"""Clinical guideline search via Tavily (geography-aware)."""

from __future__ import annotations

from typing import Dict, List

from tavily import AsyncTavilyClient

# Regulatory-body / guideline domains by geography
GUIDELINE_DOMAINS: Dict[str, List[str]] = {
    "USA": [
        "acc.org",
        "heart.org",
        "diabetes.org",
        "nih.gov",
        "cdc.gov",
        "uptodate.com",
        "fda.gov",
    ],
    "Germany": [
        "awmf.org",
        "escardio.org",
        "dgk.org",
        "aerzteblatt.de",
        "ema.europa.eu",
    ],
    "EU": [
        "escardio.org",
        "ema.europa.eu",
        "nice.org.uk",
        "easl.eu",
    ],
    "India": [
        "icmr.nic.in",
        "cdsco.gov.in",
        "apiindia.org",
    ],
    "UK": [
        "nice.org.uk",
        "bnf.nice.org.uk",
        "gov.uk",
    ],
}


async def search_guidelines(
    query: str,
    country: str = "USA",
    api_key: str = "",
    max_results: int = 5,
) -> List[Dict]:
    """
    Search for clinical practice guidelines relevant to a geography.

    Args:
        query:       Clinical search query.
        country:     Physician's country — determines which guideline sources to use.
        api_key:     Tavily API key.
        max_results: Number of results to return.

    Returns:
        List of dicts with title, url, content snippet.
    """
    if not api_key:
        return []

    client = AsyncTavilyClient(api_key=api_key)
    domains = GUIDELINE_DOMAINS.get(country, GUIDELINE_DOMAINS["USA"])

    try:
        response = await client.search(
            query=f"clinical guidelines {query}",
            search_depth="advanced",
            include_domains=domains,
            max_results=max_results,
        )
    except Exception:
        return []

    results: List[Dict] = []
    for r in response.get("results", []):
        results.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", "")[:400],
        })
    return results

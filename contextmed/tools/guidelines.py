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

# Query context to append for each geography to improve search relevance
GUIDELINE_QUERY_CONTEXT: Dict[str, str] = {
    "USA": "FDA AHA ACC guidelines United States",
    "Germany": "AWMF Leitlinie deutsche guidelines Germany EMA",
    "EU": "ESC EMA European guidelines",
    "India": "ICMR CDSCO Indian guidelines India",
    "UK": "NICE BNF NHS guidelines United Kingdom",
}

# Additional domains for critical care searches
CRITICAL_CARE_DOMAINS: List[str] = [
    "sccm.org",           # Society of Critical Care Medicine
    "esicm.org",          # European Society of Intensive Care Medicine
    "intensivecarenetwork.com",
    "ccforum.biomedcentral.com",  # Critical Care Forum
    "pmc.ncbi.nlm.nih.gov",       # PubMed Central for research
]


async def search_guidelines(
    query: str,
    country: str = "USA",
    api_key: str = "",
    max_results: int = 5,
    critical_mode: bool = False,
) -> List[Dict]:
    """
    Search for clinical practice guidelines relevant to a geography.

    Args:
        query:         Clinical search query.
        country:       Physician's country — determines which guideline sources to use.
        api_key:       Tavily API key.
        max_results:   Number of results to return.
        critical_mode: If True, include critical care/emergency domains and context.

    Returns:
        List of dicts with title, url, content snippet.
    """
    if not api_key:
        return []

    client = AsyncTavilyClient(api_key=api_key)
    domains = GUIDELINE_DOMAINS.get(country, GUIDELINE_DOMAINS["USA"]).copy()
    query_context = GUIDELINE_QUERY_CONTEXT.get(country, GUIDELINE_QUERY_CONTEXT["USA"])

    # Add critical care domains and context for critical mode
    if critical_mode:
        domains.extend(CRITICAL_CARE_DOMAINS)
        query_context += " critical care emergency ICU intensive care SCCM"

    # Build geography-aware query to improve relevance
    enhanced_query = f"{query} {query_context} clinical practice guidelines"

    try:
        response = await client.search(
            query=enhanced_query,
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

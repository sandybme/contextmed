"""PubMed literature search via NCBI E-Utilities (free, no API key needed)."""

from __future__ import annotations

from typing import Dict, List

import aiohttp


async def search_pubmed(
    terms: List[str],
    max_results: int = 5,
    timeout_seconds: int = 15,
) -> List[Dict]:
    """
    Search PubMed and return article summaries.

    Args:
        terms:           Search keywords.
        max_results:     Maximum articles to return.
        timeout_seconds: HTTP request timeout.

    Returns:
        List of dicts with title, authors, source, pubdate, url.
    """
    results: List[Dict] = []
    query = "+".join(terms[:5])
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        # Step 1: Search for PubMed IDs
        search_url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            f"?db=pubmed&term={query}&retmax={max_results}&retmode=json"
        )
        async with session.get(search_url) as resp:
            if resp.status != 200:
                return results
            data = await resp.json()

        ids = data.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return results

        # Step 2: Fetch summaries for those IDs
        summary_url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            f"?db=pubmed&id={','.join(ids)}&retmode=json"
        )
        async with session.get(summary_url) as resp:
            if resp.status != 200:
                return results
            summaries = await resp.json()

        for pmid in ids:
            article = summaries.get("result", {}).get(pmid, {})
            if not isinstance(article, dict):
                continue
            authors = article.get("authors", [])
            results.append({
                "title": article.get("title", ""),
                "authors": ", ".join(
                    a.get("name", "") for a in authors[:3]
                ),
                "source": article.get("source", ""),
                "pubdate": article.get("pubdate", ""),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            })

    return results

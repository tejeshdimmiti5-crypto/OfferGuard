"""Deterministic comparable-employer recommendations.

This module is deliberately separate from the risk engine. Recommendations never
change the OfferGuard outcome or score. URLs are official employer career pages;
the app does not claim that a vacancy is currently open.
"""

import re

COMPANIES = [
    {
        "name": "Microsoft",
        "domain": "microsoft.com",
        "careers_url": "https://careers.microsoft.com/",
        "roles": {"software", "developer", "data", "ai", "machine learning", "cloud", "security", "analyst", "intern"},
    },
    {
        "name": "Google",
        "domain": "google.com",
        "careers_url": "https://www.google.com/about/careers/",
        "roles": {"software", "developer", "data", "ai", "machine learning", "cloud", "security", "analyst", "intern"},
    },
    {
        "name": "Amazon",
        "domain": "amazon.com",
        "careers_url": "https://www.amazon.jobs/",
        "roles": {"software", "developer", "data", "ai", "machine learning", "cloud", "security", "analyst", "intern"},
    },
    {
        "name": "IBM",
        "domain": "ibm.com",
        "careers_url": "https://www.ibm.com/careers",
        "roles": {"software", "developer", "data", "ai", "machine learning", "cloud", "security", "analyst", "consulting", "intern"},
    },
    {
        "name": "Oracle",
        "domain": "oracle.com",
        "careers_url": "https://www.oracle.com/careers/",
        "roles": {"software", "developer", "data", "ai", "cloud", "security", "analyst", "intern"},
    },
    {
        "name": "Accenture",
        "domain": "accenture.com",
        "careers_url": "https://www.accenture.com/in-en/careers",
        "roles": {"software", "developer", "data", "ai", "cloud", "security", "analyst", "consulting", "intern"},
    },
    {
        "name": "Deloitte",
        "domain": "deloitte.com",
        "careers_url": "https://www.deloitte.com/careers",
        "roles": {"software", "developer", "data", "ai", "cloud", "security", "analyst", "consulting", "intern"},
    },
    {
        "name": "TCS",
        "domain": "tcs.com",
        "careers_url": "https://www.tcs.com/careers",
        "roles": {"software", "developer", "data", "ai", "cloud", "security", "analyst", "consulting", "intern"},
    },
    {
        "name": "Infosys",
        "domain": "infosys.com",
        "careers_url": "https://www.infosys.com/careers/",
        "roles": {"software", "developer", "data", "ai", "cloud", "security", "analyst", "consulting", "intern"},
    },
    {
        "name": "Wipro",
        "domain": "wipro.com",
        "careers_url": "https://careers.wipro.com/",
        "roles": {"software", "developer", "data", "ai", "cloud", "security", "analyst", "consulting", "intern"},
    },
]

ROLE_TERMS = (
    "software", "developer", "engineer", "data", "analyst", "machine learning",
    "artificial intelligence", "ai", "cloud", "devops", "cyber", "security",
    "consulting", "intern", "internship", "frontend", "backend", "full stack",
)


def _role_terms(text: str) -> set[str]:
    lowered = text.lower()
    return {term for term in ROLE_TERMS if term in lowered}


def recommend_companies(text: str, limit: int = 5) -> list[dict]:
    """Return comparable employers for the detected role.

    This is a deterministic reference list, not a live job feed. The returned
    careers_url always points to an employer's official careers site.
    """
    terms = _role_terms(text)
    lowered = text.lower()
    scored = []

    for company in COMPANIES:
        if company["domain"] in lowered:
            continue
        overlap = len(terms & company["roles"])
        scored.append((overlap, company["name"], company))

    scored.sort(key=lambda item: (-item[0], item[1]))
    selected = []
    for overlap, _, company in scored[:limit]:
        selected.append({
            "company": company["name"],
            "careers_url": company["careers_url"],
            "match": "Strong role match" if overlap >= 2 else "Comparable employer",
            "verified_source": company["domain"],
            "live_opening": False,
        })
    return selected

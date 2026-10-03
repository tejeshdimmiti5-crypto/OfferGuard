from analysis.signals import detect, INFO
from extraction.text import normalize, entities

DISCLAIMER = "These are automated risk signals, not a verdict about any company or person. Always verify through official channels."

def assess(text: str, official_listing_verified: bool | None = None):
    text = normalize(text)
    evidence = detect(text)
    score = sum(item.weight for item in evidence)
    risk = "HIGH" if any(item.strength == "strong" for item in evidence) or score >= 5 else "MEDIUM" if score >= 2 else "LOW"

    if risk == "HIGH" or (risk == "MEDIUM" and len(evidence) >= 2):
        outcome = "RISK_DETECTED"
    elif official_listing_verified is True and risk == "LOW":
        outcome = "VERIFIED"
    else:
        outcome = "UNCONFIRMED"

    facts = entities(text)
    uncertainty = []
    if official_listing_verified is None:
        uncertainty.append("No independent official job-listing verification was supplied.")
    if not facts["emails"]:
        uncertainty.append("No sender email address was found, so the sender domain could not be checked.")
    uncertainty.append("The deterministic engine evaluates extracted text; absence of warning signs is not proof that an offer is genuine.")

    actions = list(dict.fromkeys(INFO[item.signal][4] for item in evidence))
    actions.append("Never pay money to get a job or internship. Confirm the offer on the company's official website first.")

    return {
        "outcome": outcome,
        "risk": risk,
        "score": score,
        "evidence": [item.as_dict() | {"name": INFO[item.signal][0]} for item in evidence],
        "why": [INFO[item.signal][3] for item in evidence],
        "facts": {"emails": facts["emails"], "link_domains": facts["link_domains"]},
        "actions": actions,
        "uncertainty": uncertainty,
        "disclaimer": DISCLAIMER,
    }

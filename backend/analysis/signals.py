import re
from models.schema import Evidence
from extraction.text import normalize, split_sentences, entities
from verification import domains as D

INFO = {
    "R01": ("Asks the candidate to send money", 5, "strong", "The message asks the candidate to send money.", "Do not pay. Verify the offer through an official company channel."),
    "R02": ("Recruitment fee or deposit", 5, "strong", "The message requests a recruitment, registration, training, or security fee.", "Do not pay. Contact the company using a phone number or website you found yourself."),
    "R03": ("Unusual sender domain", 2, "normal", "The sender domain has characteristics often seen in suspicious recruiting messages.", "Find the company's real website and compare the domain letter by letter."),
    "R04": ("Known company mentioned with a non-official contact domain", 4, "normal", "A company name is mentioned but the contact domain is not one of its configured official domains.", "Open the company's official careers site yourself and verify the recruiter and role."),
    "R05": ("Official job listing not found", 0, "normal", "Automatic listing lookup is not enabled in this release.", "Search the company's own careers page for the exact role."),
    "R06": ("Pay looks unusually high for the role", 2, "normal", "The advertised pay is unusually high for a low-experience or basic role.", "Compare compensation with the company's published role details and typical pay."),
    "R07": ("Urgency or pressure", 1, "normal", "The message pressures the candidate to act immediately.", "Slow down and verify before responding."),
    "R08": ("Personal email or chat app used for recruiting", 1, "normal", "The recruiter uses a personal email address or chat app for hiring communication.", "Ask for a company email and independently confirm the sender."),
    "R09": ("Suspicious link", 2, "normal", "The message contains a shortened, unusual, or raw-IP link.", "Do not click it. Type the company's official website yourself."),
    "R10": ("Asks for sensitive documents or credentials", 2, "normal", "The message requests identity, bank, password, PIN, or one-time-code data.", "Do not share sensitive information until the offer is independently verified."),
    "R11": ("Different company domains in one message", 1, "normal", "Contact addresses appear on unrelated company domains.", "Check which domain belongs to the actual company."),
    "R12": ("Offer-letter formatting or content problem", 0, "normal", "Automatic visual/layout checks are not enabled in this release.", "Compare the document against information from the company's official channels."),
}

NEG = re.compile(r"\b(no|not|never|without|zero|nor|don't|do not|doesn't|does not|free of)\b|n't\b", re.I)
MONEY = re.compile(r"(?:₹|\brs\b\.?|\binr\b|\brupees\b)\s*\d|\d[\d,]*\s*(?:rs\b|rupees|inr|/-)", re.I)
FEE = re.compile(r"\b(?:registration|processing|training|kit|laptop|security|refundable|verification|onboarding|joining|admin|application|document|courier|id[- ]card|interview|seat|booking|activation)\s+(?:fee|fees|charge|charges|deposit|amount|payment)\b|\bsecurity deposit\b", re.I)
PAY_TO = re.compile(r"\b(?:pay|deposit|transfer|send|remit)\b[^.\n]{0,80}\b(?:upi|gpay|google pay|phonepe|paytm|bank account|our account|qr)\b|\b(?:you|candidate|applicant)\b[^.\n]{0,30}\b(?:have to|need to|must|should|will need to)\b\s+(?:pay|deposit|transfer)\b|\b(?:kindly|please)\s+(?:pay|deposit|transfer)\b", re.I)
PAY_OK = re.compile(r"stipend|salary|bonus|reimburs|refund(?!able)|will be (?:paid|credited|transferred|deposited)|credited to your", re.I)
ASK = re.compile(r"\b(?:send|share|provide|submit|upload|give|tell|enter|forward|reply with)\b", re.I)
SENS_STRONG = re.compile(r"\b(?:otp|cvv|upi pin|atm pin|pin number|password|card number|card details|net ?banking)\b", re.I)
SENS = re.compile(r"\b(?:aadhaar|aadhar|pan card|pan number|passport|bank account|account number|ifsc|cancelled cheque)\b", re.I)
URGENT = re.compile(r"\b(?:urgent(?:ly)?|immediately|asap|last chance|today only|limited (?:seats|slots|vacancies)|offer (?:will )?expires?|within (?:2|6|12|24|48) ?(?:hours|hrs)|by (?:today|tonight|end of day)|hurry|act now|confirm (?:now|today)|only \d+ (?:seats|slots))\b", re.I)
CHANNEL = re.compile(r"\b(?:whatsapp|telegram)\b", re.I)
HIRING = re.compile(r"\b(?:hr|recruit\w*|hiring|hire|job|opportunity|offer|selected|contact)\b", re.I)
CUES1 = re.compile(r"no experience|without experience|any graduate|any degree|typing|data entry|copy[- ]?paste|part[- ]time|10th|12th|no skills|home based|simple tasks|review(?:ing)? products", re.I)
CUES2 = re.compile(r"fresher|intern|work from home|wfh", re.I)
AMOUNT = re.compile(r"(?:₹|\brs\b\.?|\binr\b)\s*([\d,]+)|([\d,]+)\s*(?:rs\b|rupees|inr|/-)", re.I)
MONTHLY = re.compile(r"per month|/ ?month|monthly|a month", re.I)
DAILY = re.compile(r"\b(?:daily|per day|a day|every day)\b", re.I)
LPA = re.compile(r"(\d+(?:\.\d+)?)\s*lpa", re.I)

def _amounts(text):
    result = []
    for match in AMOUNT.finditer(text):
        raw = (match.group(1) or match.group(2)).replace(",", "")
        if raw.isdigit(): result.append(int(raw))
    return result

def detect(text):
    text = normalize(text)
    ents = entities(text)
    found = {}
    def add(signal, quote, claim, weight=None, strength=None):
        w = INFO[signal][1] if weight is None else weight
        current = found.get(signal)
        if current is None or w > current.weight:
            found[signal] = Evidence(signal, claim, quote[:200], w, strength or INFO[signal][2])

    low_text = text.lower()
    tier1, tier2 = bool(CUES1.search(low_text)), bool(CUES2.search(low_text))
    for sentence in split_sentences(text):
        low, neg = sentence.lower(), bool(NEG.search(sentence.lower()))
        if not neg and FEE.search(low): add("R02", sentence, "Mentions a fee or deposit the candidate is expected to pay")
        elif not neg and PAY_TO.search(low) and MONEY.search(low) and not PAY_OK.search(low): add("R01", sentence, "Asks the candidate to send money")
        if not neg and SENS_STRONG.search(low) and ASK.search(low): add("R10", sentence, "Asks for a one-time code, PIN or password", weight=5, strength="strong")
        elif not neg and SENS.search(low) and ASK.search(low): add("R10", sentence, "Asks for identity or bank details")
        if URGENT.search(low): add("R07", sentence, "Uses urgency or a short deadline")
        if CHANNEL.search(low) and HIRING.search(low): add("R08", sentence, "Recruiting through a chat app")
        amounts = _amounts(low)
        limit = 40000 if tier1 else 100000 if tier2 else None
        if (limit and MONTHLY.search(low) and any(value >= limit for value in amounts)) or (DAILY.search(low) and any(value >= 3000 for value in amounts)):
            add("R06", sentence, "Pay looks unusually high for the role described")
        lpa = LPA.search(low)
        if lpa and float(lpa.group(1)) >= 40 and (tier1 or tier2): add("R06", sentence, "Annual pay looks unusually high for the role described")

    for email, domain in zip(ents["emails"], ents["email_domains"]):
        if D.is_freemail(domain): add("R08", email, "Recruiter uses a personal email address")
        elif D.is_risky_domain(domain): add("R03", email, "Sender domain looks unusual for a company")
    for brand in D.brand_mentions(text):
        if ents["email_domains"] and not any(D.is_official(domain, brand) for domain in ents["email_domains"]):
            add("R04", ents["emails"][0], f"Mentions {brand.title()}, but no contact address is on its official domain")
    for url, domain in zip(ents["urls"], ents["link_domains"]):
        if D.is_shortener(domain) or D.is_risky_domain(domain): add("R09", url, "Link is shortened or uses an unusual address")
    bases = {".".join(domain.split(".")[-2:]) for domain in ents["email_domains"] if not D.is_freemail(domain)}
    if len(bases) >= 2: add("R11", " and ".join(ents["emails"][:2]), "Contact addresses are on different company domains")
    if "R02" in found: found.pop("R01", None)
    return sorted(found.values(), key=lambda evidence: (-evidence.weight, evidence.signal))

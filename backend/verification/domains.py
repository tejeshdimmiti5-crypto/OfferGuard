import re

FREEMAIL = {"gmail.com", "yahoo.com", "yahoo.in", "outlook.com", "hotmail.com", "rediffmail.com", "proton.me", "protonmail.com", "icloud.com", "live.com", "aol.com", "mail.com"}
RISKY_TLDS = {"xyz", "top", "click", "work", "site", "buzz", "icu", "cyou", "monster", "rest", "sbs", "cfd", "live", "shop"}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.ly", "cutt.ly", "rb.gy", "is.gd", "goo.gl"}
BRANDS = {
    "tcs": {"tcs.com"}, "infosys": {"infosys.com"}, "wipro": {"wipro.com"}, "google": {"google.com"},
    "microsoft": {"microsoft.com"}, "amazon": {"amazon.com", "amazon.jobs", "amazon.in"},
    "accenture": {"accenture.com"}, "cognizant": {"cognizant.com"}, "capgemini": {"capgemini.com"},
    "hcl": {"hcltech.com", "hcl.com"}, "ibm": {"ibm.com"}, "deloitte": {"deloitte.com"},
    "flipkart": {"flipkart.com"}, "tech mahindra": {"techmahindra.com"},
}

def is_freemail(domain): return domain in FREEMAIL
def is_ip(domain): return bool(re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", domain))

def is_risky_domain(domain):
    label = domain.split(".")[0]
    return (
        domain.rsplit(".", 1)[-1] in RISKY_TLDS
        or "xn--" in domain
        or is_ip(domain)
        or ("-" in label and bool(re.search(r"hr|career|jobs?|recruit|hiring|offer|selection|hire", label)))
        or bool(re.search(r"\d{3,}", label))
    )

def is_shortener(domain): return domain in SHORTENERS
def brand_mentions(text): return [brand for brand in BRANDS if re.search(rf"\b{re.escape(brand)}\b", text, re.I)]
def is_official(domain, brand): return any(domain == official or domain.endswith("." + official) for official in BRANDS[brand])

import re
import unicodedata
from urllib.parse import urlparse

EMAIL = re.compile(r"[\w.+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)")
URL = re.compile(r"(?:https?://|www\.)[^\s<>\"')]+|\b(?:bit\.ly|tinyurl\.com|t\.ly|cutt\.ly|rb\.gy|is\.gd|goo\.gl)/[^\s<>\"')]+", re.I)

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").replace("\u00a0", " ")
    return re.sub(r"[ \t]+", " ", text).strip()

def split_sentences(text: str):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]

def entities(text: str):
    emails = [m.group(0).rstrip(".") for m in EMAIL.finditer(text)]
    email_domains = [m.group(1).rstrip(".").lower() for m in EMAIL.finditer(text)]
    urls = [u.rstrip(".,;:!?") for u in URL.findall(text)]
    link_domains = []
    for url in urls:
        host = urlparse(url if url.lower().startswith("http") else "http://" + url).hostname or ""
        link_domains.append(host.lower().removeprefix("www."))
    return {"emails": emails, "email_domains": email_domains, "urls": urls, "link_domains": link_domains}

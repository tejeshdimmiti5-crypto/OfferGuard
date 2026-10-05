import json
import os

SYSTEM = """You explain the evidence already produced by a job-offer risk engine. Use only the supplied evidence and uncertainty. Never add new factual claims. Never declare a company or person fraudulent and never override the deterministic outcome. Respond with valid JSON containing summary (string) and actions (array of strings, max 4).

LANGUAGE RULES:
- If requested language is Telugu, every user-facing word in summary and every action MUST be written in natural Telugu script (తెలుగు). Do not answer in English, Hindi, transliterated Telugu, or Telugu written with Latin letters.
- Keep company names, email addresses, URLs, signal IDs, and exact evidence quotes unchanged when they must be shown.
- If requested language is English, write in English.
- Do not translate the deterministic outcome value itself; the UI handles that separately."""

def explain(assessment: dict, language: str = "en"):
    from openai import OpenAI
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    api_key = os.environ["AZURE_OPENAI_API_KEY"]
    deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]
    client = OpenAI(api_key=api_key, base_url=f"{endpoint}/openai/v1/")
    payload = {key: assessment[key] for key in ("outcome", "risk", "evidence", "uncertainty")}
    response = client.chat.completions.create(
        model=deployment,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": json.dumps({"requested_language": "Telugu (తెలుగు script)" if language == "te" else "English", "assessment": payload}, ensure_ascii=False)},
        ],
    )
    parsed = json.loads(response.choices[0].message.content or "{}")
    summary, actions = parsed.get("summary"), parsed.get("actions")
    if not isinstance(summary, str) or not isinstance(actions, list) or not all(isinstance(item, str) for item in actions):
        return None

    if language == "te":
        # Refuse an accidental English/Latin-script answer so the UI never
        # labels an English explanation as Telugu.
        user_text = " ".join([summary, *actions])
        telugu_chars = sum("\u0c00" <= ch <= "\u0c7f" for ch in user_text)
        if telugu_chars < 8:
            return None

    return {"summary": summary[:1000], "actions": actions[:4]}

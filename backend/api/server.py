import os
import time
from collections import defaultdict, deque

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from analysis.assess import assess

MAX_TEXT = 8000
MAX_FILE = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"application/pdf", "image/png", "image/jpeg"}
RATE_WINDOW = 60
RATE_LIMIT = 20
visits = defaultdict(deque)

app = FastAPI(title="OfferGuard API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class AssessRequest(BaseModel):
    text: str = Field(default="", max_length=MAX_TEXT)
    language: str = Field(default="en", pattern="^(en|te)$")
    official_listing_verified: bool | None = None
    explain: bool = False

class HealthResponse(BaseModel):
    status: str
    document_intelligence: bool
    azure_openai: bool

@app.get("/")
def root():
    return {
        "name": "OfferGuard API",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "assessment": "/api/assess",
        "file_assessment": "/api/assess-file",
    }

@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        document_intelligence=bool(os.getenv("AZURE_DOCINTEL_ENDPOINT") and os.getenv("AZURE_DOCINTEL_KEY")),
        azure_openai=bool(os.getenv("AZURE_OPENAI_ENDPOINT") and os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_DEPLOYMENT")),
    )

def client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"

def check_rate_limit(key: str):
    now = time.time()
    q = visits[key]
    while q and now - q[0] > RATE_WINDOW:
        q.popleft()
    if len(q) >= RATE_LIMIT:
        raise HTTPException(429, "Too many requests. Please try again shortly.")
    q.append(now)

def validate_file(data: bytes, content_type: str):
    if len(data) > MAX_FILE:
        raise HTTPException(413, "File exceeds the 10 MB limit.")
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(415, "Only PDF, PNG, and JPEG files are supported.")
    signatures = {
        "application/pdf": data[:5] == b"%PDF-",
        "image/png": data[:8] == b"\x89PNG\r\n\x1a\n",
        "image/jpeg": data[:3] == b"\xff\xd8\xff",
    }
    if not signatures[content_type]:
        raise HTTPException(415, "The file signature does not match its declared content type.")

@app.post("/api/assess")
def assess_text(payload: AssessRequest, request: Request):
    check_rate_limit(client_key(request))
    if not payload.text.strip():
        raise HTTPException(400, "Paste the recruitment message or offer text first.")
    result = assess(payload.text, payload.official_listing_verified)
    return add_ai_explanation(result, payload.language, payload.explain)

@app.post("/api/assess-file")
def assess_file(
    request: Request,
    file: UploadFile = File(...),
    language: str = Form("en"),
    official_listing_verified: bool | None = Form(None),
    explain: bool = Form(False),
):
    check_rate_limit(client_key(request))
    if language not in {"en", "te"}:
        raise HTTPException(400, "language must be 'en' or 'te'.")
    content_type = file.content_type or "application/octet-stream"
    data = file.file.read(MAX_FILE + 1)
    validate_file(data, content_type)
    if not os.getenv("AZURE_DOCINTEL_ENDPOINT") or not os.getenv("AZURE_DOCINTEL_KEY"):
        raise HTTPException(503, "Azure Document Intelligence is not configured. Paste the text instead.")
    try:
        from extraction.azure_document import read_document
        text = read_document(data, content_type)
    except Exception:
        raise HTTPException(502, "Could not read the file with Document Intelligence. Please paste the text instead.")
    text = text[:MAX_TEXT]
    if not text.strip():
        raise HTTPException(422, "No readable text was found in the file.")
    result = assess(text, official_listing_verified)
    result["extracted_text"] = text
    return add_ai_explanation(result, language, explain)

def _telugu_fallback(result):
    outcome = result.get("outcome")
    risk = result.get("risk")
    if outcome == "RISK_DETECTED":
        summary = "ఈ ఉద్యోగ ఆఫర్‌లో ప్రమాదానికి సంబంధించిన కొన్ని సంకేతాలు గుర్తించబడ్డాయి. దిగువ చూపిన ఆధారాలను పరిశీలించి, కంపెనీ అధికారిక వెబ్‌సైట్ ద్వారా స్వతంత్రంగా ధృవీకరించండి."
    elif outcome == "VERIFIED":
        summary = "అందించిన సమాచారంలో తక్కువ ప్రమాదం కనిపించింది మరియు అధికారిక ఉద్యోగ ధృవీకరణ అందించబడింది. అయినప్పటికీ, తుది నిర్ణయం తీసుకునే ముందు అధికారిక ఛానల్ ద్వారా ధృవీకరించండి."
    else:
        summary = "ఈ ఆఫర్‌ను పూర్తిగా ధృవీకరించడానికి సరిపడిన స్వతంత్ర ఆధారాలు లేవు. కంపెనీ అధికారిక కెరీర్ వెబ్‌సైట్ ద్వారా ఉద్యోగాన్ని ధృవీకరించండి."
    actions = [
        "ఉద్యోగం కోసం ఎటువంటి డబ్బు చెల్లించవద్దు.",
        "కంపెనీ అధికారిక వెబ్‌సైట్‌లో అదే ఉద్యోగాన్ని తనిఖీ చేయండి.",
        "వ్యక్తిగత లేదా బ్యాంకింగ్ సమాచారాన్ని పంపించే ముందు అధికారిక ఛానల్‌ను నిర్ధారించండి.",
        "ప్రస్తుత ప్రమాద స్థాయి: " + str(risk or "తెలియదు") + ".",
    ]
    return {"summary": summary, "actions": actions}

def add_ai_explanation(result, language, explain_requested):
    if explain_requested and os.getenv("AZURE_OPENAI_ENDPOINT") and os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_DEPLOYMENT"):
        try:
            from analysis.azure_explain import explain
            result["ai_explanation"] = explain(result, language)
        except Exception:
            result["ai_explanation"] = None
    else:
        result["ai_explanation"] = None

    if language == "te" and result["ai_explanation"] is None:
        result["ai_explanation"] = _telugu_fallback(result)
    return result

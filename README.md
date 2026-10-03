# OfferGuard

OfferGuard is an explainable job-offer risk assessment system. It accepts recruiter text and PDF/PNG/JPEG documents, uses Azure AI Document Intelligence for OCR when configured, applies deterministic evidence rules, and can use Azure OpenAI only to explain evidence in English or Telugu.

## Decision boundary

**AI never decides the outcome.** The deterministic rules engine owns the outcome. Every detected signal contains an exact quote from the supplied content. The absence of warning signs is never treated as proof that an offer is genuine.

The **Verified** state requires a user-supplied independent confirmation that the exact role was found on the employer's official careers site, and only appears when deterministic risk is low. OfferGuard does not perform or claim that external lookup.

## Outcomes

- \`VERIFIED\` — low deterministic risk + user-supplied official-listing verification.
- \`UNCONFIRMED\` — insufficient evidence to verify the offer.
- \`RISK_DETECTED\` — deterministic evidence crossed the risk threshold.

## Architecture

\`\`\`
Flutter client
    |
    v
FastAPI backend
    |
    +--> text normalization + entity extraction
    +--> deterministic R01-R12 evidence engine
    |       +--> exact quotes
    |       +--> weights / severity
    |       +--> final outcome
    |
    +--> Azure AI Document Intelligence (optional OCR)
    |
    +--> Azure OpenAI (optional explanation only)
\`\`\`

## Deterministic signals

The engine covers recruitment fees, direct money requests, unusual sender domains, company-name/domain mismatch, unrealistic pay, urgency, personal-email/chat recruiting, suspicious links, sensitive-data requests, and mixed company domains. Automatic official job-listing lookup and automatic visual layout scoring are intentionally outside the decision boundary in this release.

## Backend

\`\`\`bash
python -m venv .venv
# Windows: .venv\\\\Scripts\\\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
\`\`\`

Health: \`http://localhost:8000/health\`

Text assessment: \`POST /api/assess\`

\`\`\`json
{
  "text": "Pay Rs 999 registration fee through UPI.",
  "language": "en",
  "official_listing_verified": null,
  "explain": true
}
\`\`\`

File assessment: \`POST /api/assess-file\` as multipart form-data. Files are capped at 10 MB and their file signatures are checked before OCR.

## Flutter frontend

The frontend source is in \`flutter_app/\`. The project uses \`http\` 1.6.0 and \`file_picker\` 13.1.0.

Generate the platform scaffolding once with the Flutter SDK:

\`\`\`bash
cd flutter_app
flutter create --platforms=android,ios,web .
flutter pub get
flutter run --dart-define=API_BASE_URL=http://localhost:8000
\`\`\`

For an Android emulator use \`http://10.0.2.2:8000\` as the API base URL.

## Azure configuration

### Document Intelligence

Set \`AZURE_DOCINTEL_ENDPOINT\` and \`AZURE_DOCINTEL_KEY\`. The backend uses the GA \`2024-11-30\` Document Intelligence REST API and \`prebuilt-read\`, posting an analyze request and polling the returned \`Operation-Location\`.

### Azure OpenAI

Set \`AZURE_OPENAI_ENDPOINT\`, \`AZURE_OPENAI_API_KEY\`, and \`AZURE_OPENAI_DEPLOYMENT\`. The explanation layer uses the Azure OpenAI v1 endpoint through the standard OpenAI Python client and never receives authority over the deterministic outcome.

## Tests and evaluation

\`\`\`bash
python -m unittest discover -s tests
python backend/evaluate.py
\`\`\`

The shipped evaluation set is synthetic and is not a real-world accuracy claim. The current local synthetic harness reports 20 scored examples, 0 false positives, and 80% recall for the deterministic risk flagger.

## Security boundary

Do not commit API keys, real recruitment records, identity documents, passwords, OTPs, or bank information. The backend does not log submitted content and applies file type/signature checks, size limits, rate limiting, and deterministic decision boundaries.

## Disclaimer

OfferGuard is an assistive verification tool. It cannot guarantee that an offer is genuine or fraudulent. Independently verify employers and roles through official channels before paying money or sharing sensitive information.

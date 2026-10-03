# OfferGuard

> **Evidence-first job-offer risk assessment with a strict AI decision boundary.**

OfferGuard helps candidates examine recruitment messages and offer documents for concrete warning signals before they pay money, click suspicious links, or share sensitive information.

It combines a **deterministic risk engine** with **Azure AI Document Intelligence** for document extraction and **Azure OpenAI** for optional multilingual explanation. The model can explain evidence, but **it never decides the final outcome**.

<p align="center">
  <strong>Evidence first · Uncertainty visible · AI never decides</strong>
</p>

---

## Live demo

**Web app:** https://offerguard-web.onrender.com

**API health:** https://offerguard-api-joh9.onrender.com/health

**Source:** https://github.com/tejeshdimmiti5-crypto/OfferGuard

> The public demo uses the Render deployment configured for this repository. Azure services remain optional until their credentials are configured.

## Why OfferGuard?

Recruitment scams often rely on urgency, payment requests, impersonation, suspicious domains, unrealistic compensation, and requests for sensitive information.

A useful verification tool should not simply return a black-box "scam / not scam" label. It should show:

- **what was detected**
- **the exact source text that triggered it**
- **how the deterministic score was formed**
- **what could not be independently verified**
- **what the candidate should do next**

That is the core design of OfferGuard.

---

## Core principle

### AI explains. Rules decide.

~~~
Input
  │
  ├── Recruiter text
  └── PDF / PNG / JPEG
          │
          ▼
Azure AI Document Intelligence
          │
          ▼
Text normalization + entity extraction
          │
          ▼
Deterministic R01–R12 signal engine
          │
          ├── exact quote
          ├── signal
          ├── weight
          └── severity
          │
          ▼
Deterministic risk + outcome
          │
          ├── VERIFIED
          ├── UNCONFIRMED
          └── RISK_DETECTED
          │
          └──────────────► Optional Azure OpenAI explanation
                           (cannot change the outcome)
~~~

The system never treats the absence of warning signs as proof that an offer is genuine.

---

## Outcomes

| Outcome | Meaning |
|---|---|
| **VERIFIED** | Deterministic risk is low **and** the user supplied an independent confirmation that the exact role exists on the employer's official careers site. |
| **UNCONFIRMED** | There is not enough evidence to establish authenticity. |
| **RISK_DETECTED** | Deterministic evidence crossed the configured risk threshold. |

### Important verification boundary

OfferGuard does **not** pretend that it has checked an employer's external careers site.

The **Verified** state depends on a user-supplied confirmation:

> "I independently verified the exact role on the official careers site."

That check remains outside the AI decision boundary.

---

## Features

### Deterministic evidence engine
- 12 documented signals (R01–R12)
- weighted scoring
- severity levels
- exact source quotes
- deterministic outcome selection
- explicit uncertainty
- safe next-step recommendations

### Document analysis
Accepts:
- recruiter messages / email text
- PDF
- PNG
- JPEG

For documents, OfferGuard can use **Azure AI Document Intelligence** to extract readable text before running the deterministic engine.

### Multilingual explanation
Azure OpenAI can optionally produce:
- an evidence summary
- concise actions
- English or Telugu explanation

The explanation layer receives the existing assessment and **does not receive authority to change it**.

### Defensive handling
The API includes:
- 8,000-character text limit
- 10 MB file limit
- file signature validation
- allowed MIME-type checks
- per-client rate limiting
- controlled error responses
- CORS configuration
- no raw submitted-content logging in the application layer

### Explainable results
Each detected signal can expose:
- signal ID
- signal name
- claim
- exact quote
- weight
- severity

This makes the output auditable rather than opaque.

---

## Signal coverage

| ID | Signal |
|---|---|
| R01 | Direct request to send money |
| R02 | Recruitment fee or deposit |
| R03 | Unusual sender domain |
| R04 | Company-name / contact-domain mismatch |
| R05 | Official listing not automatically verified |
| R06 | Unusually high pay for the described role |
| R07 | Urgency or pressure |
| R08 | Personal email or chat-app recruiting |
| R09 | Suspicious or shortened link |
| R10 | Sensitive documents or credentials requested |
| R11 | Different company domains in one message |
| R12 | Offer-letter formatting/content issue |

R05 and R12 are intentionally informational in the current release and do not create a false claim of automatic external verification or visual authenticity analysis.

---

## Example

### Input

~~~
Congratulations! You are selected for our work-from-home opportunity.

Earn Rs 60,000 per month.
Please pay a refundable registration fee of Rs 1,500 through UPI.
Offer expires today.
~~~

### Evidence chain

~~~
R02  Recruitment fee or deposit
     "Please pay a refundable registration fee of Rs 1,500 through UPI."

R06  Unusually high pay
     "Earn Rs 60,000 per month."

R07  Urgency
     "Offer expires today."

RISK_DETECTED
~~~

The UI then shows the evidence, score, uncertainty, and safer next steps instead of asking an LLM to make the decision.

---

## Architecture

~~~
┌──────────────────────────────┐
│        Flutter Client        │
│   Web / mobile UI            │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│        FastAPI Backend       │
│      /api/assess             │
│      /api/assess-file        │
│      /health                 │
└──────────────┬───────────────┘
               │
       ┌───────┼───────────────┐
       │       │               │
       ▼       ▼               ▼
  Text/Entity  Azure DI      Azure OpenAI
   Extraction   OCR          Explanation
       │       │               │
       └───────┴───────┐       │
                       ▼       │
              Deterministic   │
              R01–R12 Engine  │
                       │       │
                       └───┬───┘
                           ▼
                    Final Assessment
~~~

### Technology stack

**Frontend**
- Flutter
- Material 3
- http
- file_picker

**Backend**
- Python
- FastAPI
- Uvicorn
- Pydantic

**Microsoft Azure**
- Azure AI Document Intelligence
- Azure OpenAI

**Quality**
- Python unittest
- synthetic evaluation harness
- GitHub Actions CI

**Deployment**
- Render
- GitHub

---

## Repository structure

~~~
OfferGuard/
├── backend/
│   ├── analysis/
│   │   ├── assess.py
│   │   ├── azure_explain.py
│   │   └── signals.py
│   ├── api/
│   │   └── server.py
│   ├── extraction/
│   │   ├── azure_document.py
│   │   └── text.py
│   ├── models/
│   │   └── schema.py
│   ├── verification/
│   │   └── domains.py
│   ├── evaluate.py
│   └── main.py
│
├── flutter_app/
│   ├── lib/
│   │   └── main.dart
│   ├── test/
│   ├── web/
│   └── pubspec.yaml
│
├── data/
│   └── evaluation/
│       └── synthetic_examples.json
│
├── tests/
│   ├── test_engine.py
│   └── test_dataset.py
│
├── .github/workflows/
│   ├── ci.yml
│   └── flutter-pages.yml
│
├── Dockerfile
├── render.yaml
├── requirements.txt
├── SECURITY.md
└── README.md
~~~

---

## Run locally

### 1. Clone

~~~
git clone https://github.com/tejeshdimmiti5-crypto/OfferGuard.git
cd OfferGuard
~~~

### 2. Backend

Create a virtual environment:

~~~
python -m venv .venv
~~~

Windows:

~~~
.venv\Scripts\activate
~~~

macOS / Linux:

~~~
source .venv/bin/activate
~~~

Install dependencies:

~~~
pip install -r requirements.txt
~~~

Start the API:

~~~
uvicorn backend.main:app --reload --port 8000
~~~

Health endpoint:

~~~
http://localhost:8000/health
~~~

### 3. Flutter

~~~
cd flutter_app
flutter pub get
flutter run --dart-define=API_BASE_URL=http://localhost:8000
~~~

For an Android emulator:

~~~
API_BASE_URL=http://10.0.2.2:8000
~~~

For Flutter web:

~~~
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
~~~

---

## API

### Health

~~~
GET /health
~~~

Example:

~~~json
{
  "status": "ok",
  "document_intelligence": false,
  "azure_openai": false
}
~~~

### Text assessment

~~~
POST /api/assess
Content-Type: application/json
~~~

Example:

~~~json
{
  "text": "Pay Rs 999 registration fee through UPI.",
  "language": "en",
  "official_listing_verified": null,
  "explain": false
}
~~~

The response contains the deterministic outcome, risk level, score, evidence, extracted facts, uncertainty, actions, and disclaimer.

### File assessment

~~~
POST /api/assess-file
Content-Type: multipart/form-data
~~~

Accepted document types:
- PDF
- PNG
- JPEG

Maximum file size: **10 MB**

Document extraction requires Azure AI Document Intelligence configuration.

---

## Azure configuration

### Azure AI Document Intelligence

Set:

~~~text
AZURE_DOCINTEL_ENDPOINT=
AZURE_DOCINTEL_KEY=
AZURE_DOCINTEL_API_VERSION=2024-11-30
~~~

The current implementation uses the <code>prebuilt-read</code> model and polls the returned <code>Operation-Location</code>.

### Azure OpenAI

Set:

~~~text
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT=
~~~

Azure OpenAI is optional.

When enabled, it is used only for evidence explanation. It must not:
- create new factual evidence
- override the deterministic outcome
- declare a company or person fraudulent
- replace the uncertainty produced by the rules engine

---

## Testing

Run the backend unit tests:

~~~
python -m unittest discover -s tests
~~~

Run the synthetic evaluation:

~~~
python backend/evaluate.py
~~~

The evaluation dataset in data/evaluation/synthetic_examples.json is **synthetic**. Its results are a regression signal for the implemented rules, **not a real-world accuracy benchmark**.

The current dataset contains 21 examples, with 20 counted by the binary risk evaluation because the explicit uncertain example is excluded from that calculation.

---

## What OfferGuard does not claim

OfferGuard intentionally does **not** claim to:

- prove that a company is fraudulent
- prove that an offer is genuine from text alone
- automatically authenticate an employer's external careers website
- replace human verification
- replace legal, financial, or security advice
- provide a real-world fraud-detection accuracy percentage from the synthetic dataset

This boundary is part of the product design.

---

## Security and privacy

Never commit:

- Azure API keys
- passwords
- OTPs
- PINs
- bank information
- identity documents
- real recruitment records containing unnecessary personal data

The application is designed so the backend does not log the submitted recruitment content in its application logging path.

Additional controls include:
- file-type validation
- file-signature validation
- request size limits
- rate limiting
- deterministic decision boundaries
- controlled failure messages

See [SECURITY.md](SECURITY.md) for the project security guidance.

---

## Deployment

The project is structured for deployment as:

~~~
Flutter Web
     │
     ▼
Render Static Site
     │
     ▼
Render FastAPI Service
     │
     ├── Azure AI Document Intelligence
     └── Azure OpenAI
~~~

The repository also contains:
- `render.yaml`
- Render deployment configuration
- GitHub Actions CI
- Flutter web deployment workflow

The current public demo runs on Render:

- Web: https://offerguard-web.onrender.com
- API: https://offerguard-api-joh9.onrender.com

---

## Design decisions

### 1. Deterministic decision boundary

The most important decision in OfferGuard is not the choice of model. It is **where the model is not allowed to decide**.

The final state is produced by deterministic rules so the same input produces the same result.

### 2. Exact evidence

A signal without a source is difficult to audit.

Every fired signal therefore carries the exact text fragment that triggered it.

### 3. Visible uncertainty

"Could not verify" is a first-class result.

This prevents the system from turning missing evidence into false confidence.

### 4. Safe assistance rather than autonomous accusation

OfferGuard is designed to help a candidate slow down and verify an offer—not to make unsupported accusations about people or companies.

---

## Project status

Current scope is intentionally focused on a reliable MVP:

- ✅ deterministic risk engine
- ✅ explainable evidence chain
- ✅ PDF / PNG / JPEG extraction path
- ✅ Azure AI Document Intelligence integration
- ✅ optional Azure OpenAI explanation
- ✅ English / Telugu explanation support
- ✅ security and input hardening
- ✅ synthetic evaluation harness
- ✅ Flutter client
- ✅ Render deployment configuration
- ✅ CI configuration

Automatic external job-listing verification and automatic visual offer-letter authenticity analysis are intentionally outside the current decision boundary.

---

## Responsible-use disclaimer

OfferGuard is an **assistive verification tool**.

A VERIFIED result does not guarantee that an offer is genuine, and a RISK_DETECTED result does not by itself establish fraud. Always verify the employer, role, contact channel, and payment instructions through independently sourced official channels.

**Never pay money to obtain a job or internship. Never share passwords, OTPs, PINs, or unnecessary financial information with a recruiter.**

---

## License

MIT License. See [LICENSE](LICENSE).

---

## Repository

**GitHub:** https://github.com/tejeshdimmiti5-crypto/OfferGuard

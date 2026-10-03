# OfferGuard

OfferGuard is an explainable job-offer verification and risk-assessment system designed to help people evaluate suspicious recruitment messages, emails, screenshots, and offer documents.

## Core design

OfferGuard separates deterministic evidence and risk scoring from AI-generated interpretation.

- Evidence is extracted from the supplied material.
- Risk signals are deterministic and tied to exact source text.
- The final outcome is produced by the rules/evidence engine, not by an LLM.
- Uncertainty is explicitly surfaced as **Unconfirmed** rather than silently treated as verified.
- Azure AI Document Intelligence can be used for document/OCR extraction.
- Azure OpenAI can provide multilingual interpretation/summaries, but its output does not control the final decision.

## Visible outcomes

- **Verified**
- **Unconfirmed**
- **Risk detected**

> These outcomes are informational. OfferGuard does not guarantee that a job offer is legitimate or fraudulent.

## Safety and security

The project is designed around:

- evidence-first reasoning
- exact quoted evidence
- clear "could not verify" states
- ownership checks for protected resources
- input and file-size validation
- rate limiting
- prompt-injection boundaries for untrusted document text
- separation between user memory and document evidence
- graceful AI-provider failure handling

## Testing

The repository is intended to include unit, security, adversarial, and evaluation tests. Reported project validation included 49 passing tests and a synthetic evaluation suite with 20/20 outcome agreement in the locked MVP validation run.

## AI boundary

AI may help interpret or summarize extracted material, including multilingual/Telugu/Telugu-Hinglish content. It must not override the deterministic decision boundary.

## Disclaimer

OfferGuard is an assistive verification tool, not a substitute for contacting the employer through independently verified official channels. Always avoid sending money or sensitive identity documents until the relevant facts have been independently confirmed.

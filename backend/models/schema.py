from dataclasses import asdict, dataclass

SIGNALS = [f"R{i:02d}" for i in range(1, 13)]
LABELS = ("legitimate", "suspicious", "fraudulent", "uncertain")
INPUT_TYPES = ("screenshot", "pdf", "email", "message")

@dataclass(frozen=True)
class Evidence:
    signal: str
    claim: str
    quote: str
    weight: int
    strength: str

    def as_dict(self):
        return asdict(self)

def validate_example(ex):
    errors = [f"missing '{k}'" for k in ("id", "input_type", "label", "text", "signals") if k not in ex]
    if errors:
        return errors
    if ex["input_type"] not in INPUT_TYPES:
        errors.append(f"bad input_type {ex['input_type']!r}")
    if ex["label"] not in LABELS:
        errors.append(f"bad label {ex['label']!r}")
    if not str(ex["text"]).strip():
        errors.append("empty text")
    if not isinstance(ex["signals"], list) or any(s not in SIGNALS for s in ex["signals"]):
        errors.append("signals must be a list of R01..R12")
    return errors

def validate_dataset(items):
    report, seen = {}, set()
    for ex in items:
        errors = validate_example(ex)
        ex_id = ex.get("id", "?")
        if ex_id in seen:
            errors.append("duplicate id")
        seen.add(ex_id)
        report[ex_id] = errors
    return {k: v for k, v in report.items() if v}

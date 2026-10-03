import json
from pathlib import Path
from analysis.assess import assess
from models.schema import validate_dataset

DEFAULT = Path(__file__).resolve().parents[1] / "data" / "evaluation" / "synthetic_examples.json"

def evaluate(path=DEFAULT):
    items = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate_dataset(items)
    if errors:
        raise SystemExit(errors)
    tp = fp = fn = tn = 0
    for item in items:
        if item["label"] == "uncertain":
            continue
        predicted = assess(item["text"])["outcome"] == "RISK_DETECTED"
        actual = item["label"] in {"suspicious", "fraudulent"}
        tp += int(predicted and actual)
        fp += int(predicted and not actual)
        fn += int(not predicted and actual)
        tn += int(not predicted and not actual)
    return {"examples": tp + fp + fn + tn, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": tp / (tp + fp) if tp + fp else 0,
            "recall": tp / (tp + fn) if tp + fn else 0}

if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))

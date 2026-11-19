"""Evaluate a local Laya checkpoint against labeled real sandbox observations."""

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cyberranger.corpus import TrafficCorpus


QUESTION = {
    "classification": {
        "type": "choice",
        "instructions": "Classify this observed HTTP request as benign or malicious. Use only the request details shown.",
        "criteria": {
            "benign": "Ordinary input that does not attempt to exploit an application vulnerability.",
            "malicious": "Input that attempts SQL injection, cross-site scripting, command injection, or path traversal.",
        },
    }
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default=None)
    parser.add_argument(
        "--model",
        default=str(PROJECT_ROOT / "blue_detector" / "models" / "laya-candidate"),
    )
    args = parser.parse_args()

    cases = (TrafficCorpus(args.corpus) if args.corpus else TrafficCorpus()).labeled_cases()
    if not cases:
        raise SystemExit("No evidence-backed labeled observations are available.")
    import laya

    agent = laya.load(args.model)
    labels = ("benign", "malicious")
    counts = {label: 0 for label in labels}
    confusion = {actual: {predicted: 0 for predicted in labels} for actual in labels}
    for case in cases:
        answer = agent.predict(case["state"], QUESTION)["answers"]["classification"]["choice"]
        predicted = str(answer).lower()
        if predicted not in labels:
            raise RuntimeError(f"Unexpected Laya choice {predicted!r}")
        actual = case["label"]
        counts[actual] += 1
        confusion[actual][predicted] += 1

    total = len(cases)
    correct = sum(confusion[label][label] for label in labels)
    report = {
        "model": str(Path(args.model).resolve()),
        "n": total,
        "class_counts": counts,
        "accuracy": correct / total,
        "confusion_matrix": confusion,
        "note": "Small local corpus metrics are descriptive only and do not establish generalization.",
    }
    if counts["malicious"]:
        tp = confusion["malicious"]["malicious"]
        fp = confusion["benign"]["malicious"]
        fn = confusion["malicious"]["benign"]
        report["malicious_precision"] = tp / (tp + fp) if tp + fp else None
        report["malicious_recall"] = tp / (tp + fn) if tp + fn else None
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

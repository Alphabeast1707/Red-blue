"""Evaluate the currently loaded local detector on evidence-backed labeled observations."""

import argparse
import json
from pathlib import Path
import sys

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cyberranger.corpus import TrafficCorpus


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default=None)
    parser.add_argument("--detector", default="http://blue-detector:8000")
    args = parser.parse_args()
    corpus = TrafficCorpus(args.corpus) if args.corpus else TrafficCorpus()
    cases = corpus.labeled_cases()
    if not cases:
        raise SystemExit("No evidence-backed labeled observations are available.")

    counts = {label: 0 for label in ("benign", "malicious")}
    correct = 0
    confusion = {actual: {predicted: 0 for predicted in counts} for actual in counts}
    rows = corpus.rows()
    observations = {row["trial_id"]: row for row in rows if row.get("kind") == "observation"}
    for case in cases:
        observation = observations[case["trial_id"]]
        request = observation["request"]
        response = requests.post(
            f"{args.detector.rstrip('/')}/detect",
            json={
                "url": request["url"],
                "method": request["method"],
                "params": request.get("params", {}),
                "body": request.get("body"),
            },
            timeout=30,
        )
        response.raise_for_status()
        actual = case["label"]
        predicted = "malicious" if response.json()["flagged"] else "benign"
        counts[actual] += 1
        confusion[actual][predicted] += 1
        correct += actual == predicted

    total = len(cases)
    report = {
        "corpus": str(corpus.path),
        "n": total,
        "class_counts": counts,
        "accuracy": correct / total,
        "confusion_matrix": confusion,
        "note": "This evaluates only the currently loaded checkpoint on these labeled local observations.",
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

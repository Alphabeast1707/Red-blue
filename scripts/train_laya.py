"""Fine-tune local Laya only on captured, explicitly labeled sandbox requests."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cyberranger.corpus import TrafficCorpus

MODEL_DIR = PROJECT_ROOT / "blue_detector" / "models" / "laya"
DEFAULT_OUT = PROJECT_ROOT / "blue_detector" / "models" / "laya-candidate"


def split_cases(cases: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split by exact observed request state so repeated captures cannot leak across sets."""
    by_label: dict[str, dict[str, list[dict]]] = {"benign": {}, "malicious": {}}
    for case in cases:
        state_hash = hashlib.sha256(case["state"].encode("utf-8")).hexdigest()
        by_label[case["label"]].setdefault(state_hash, []).append(case)
    train: list[dict] = []
    evaluate: list[dict] = []
    for label, groups in by_label.items():
        ordered = sorted(groups.items(), key=lambda pair: pair[0])
        holdout_count = max(1, math.ceil(len(ordered) * 0.2))
        if len(ordered) < 2:
            raise ValueError(f"Need at least two distinct observed request states for {label}.")
        holdout_keys = {key for key, _ in ordered[-holdout_count:]}
        for key, rows in ordered:
            (evaluate if key in holdout_keys else train).extend(rows)
    return train, evaluate


def write_csv(path: Path, cases: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["state", "label"])
        writer.writeheader()
        for case in cases:
            writer.writerow({"state": case["state"], "label": case["label"]})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default=None, help="JSONL corpus path")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Local fine-tuned checkpoint directory")
    parser.add_argument("--min-per-class", type=int, default=10)
    parser.add_argument("--epochs", type=int, default=4)
    parser.add_argument("--device", choices=("auto", "cpu", "mps", "cuda"), default="auto")
    parser.add_argument("--freeze-encoder", action="store_true", help="Train only Laya's classification heads")
    parser.add_argument("--dry-run", action="store_true", help="Validate and report the split without training")
    args = parser.parse_args()

    corpus = TrafficCorpus(args.corpus) if args.corpus else TrafficCorpus()
    cases = corpus.labeled_cases()
    counts = {label: sum(case["label"] == label for case in cases) for label in ("benign", "malicious")}
    if any(count < args.min_per_class for count in counts.values()):
        raise SystemExit(
            f"Not enough evidence-backed labeled rows: {counts}. "
            f"Need at least {args.min_per_class} per class. Capture live benign controls and human-confirmed trials first."
        )
    train, evaluate = split_cases(cases)
    train_counts = {label: sum(case["label"] == label for case in train) for label in counts}
    eval_counts = {label: sum(case["label"] == label for case in evaluate) for label in counts}
    print(json.dumps({
        "corpus": str(corpus.path),
        "labeled_observations": len(cases),
        "classes": counts,
        "train_rows": len(train),
        "train_classes": train_counts,
        "held_out_rows": len(evaluate),
        "held_out_classes": eval_counts,
        "note": "These are counts from the local append-only corpus, not benchmark claims.",
    }, indent=2))
    if args.dry_run:
        return
    if not (MODEL_DIR / "model.safetensors").is_file():
        raise SystemExit(f"Base Laya checkpoint missing at {MODEL_DIR}; run scripts/download_laya.py first.")

    with tempfile.TemporaryDirectory(prefix="cyberranger-laya-") as temp_dir:
        temp = Path(temp_dir)
        train_path = temp / "train.csv"
        eval_path = temp / "heldout.csv"
        write_csv(train_path, train)
        write_csv(eval_path, evaluate)
        cli = Path(sys.executable).with_name("laya-train")
        if not cli.is_file():
            located = shutil.which("laya-train")
            if not located:
                raise SystemExit("Laya trainer entry point not found; install the optional 'laya' dependency.")
            cli = Path(located)
        command = [
            str(cli), "--data", str(train_path),
            "--text-column", "state", "--label-column", "label",
            "--base", str(MODEL_DIR), "--out", args.out,
            "--eval", str(eval_path), "--epochs", str(args.epochs),
            "--device", args.device,
        ]
        if args.freeze_encoder:
            command.append("--freeze-encoder")
        subprocess.run(command, check=True)
    print(f"Fine-tuned checkpoint saved locally at {Path(args.out).resolve()}")
    print("Review the trainer's held-out report; do not generalize from this small sandbox corpus.")


if __name__ == "__main__":
    main()

"""Download the official English Laya checkpoint into the local ignored model directory."""

from pathlib import Path
import sys

from huggingface_hub import snapshot_download

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_ROOT / "blue_detector" / "models" / "laya"


def main() -> None:
    if "huggingface_hub" not in sys.modules:
        raise RuntimeError("Install the optional dependencies with `pip install -e '.[laya]'`.")
    path = snapshot_download(
        repo_id="convaiinnovations/laya",
        local_dir=MODEL_DIR,
        allow_patterns=[
            "config.json",
            "model.safetensors",
            "rl_agent_config.json",
            "encoder/config.json",
            "tokenizer/**",
        ],
    )
    weight_path = Path(path) / "model.safetensors"
    if not weight_path.is_file():
        raise RuntimeError(f"Laya weights were not downloaded to {weight_path}")
    print(f"Downloaded official Laya English checkpoint to {MODEL_DIR}")
    print(f"Weights: {weight_path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()

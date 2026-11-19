"""Laya fine-tuning from evidence-backed, human-labeled sandbox traffic."""

from pathlib import Path
import subprocess
import sys
from typing import Optional

from cyberranger.corpus import DEFAULT_CORPUS_PATH

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAIN_SCRIPT = PROJECT_ROOT / "scripts" / "train_laya.py"
DEFAULT_MODELS_DIR = PROJECT_ROOT / "blue_detector" / "models"


class BlueLearner:
    """Runs Laya's local trainer and asks the local detector to reload its checkpoint."""

    def __init__(
        self,
        models_dir: Optional[Path | str] = None,
        detector_api_url: str = "http://blue-detector:8000",
        corpus_path: Path | str = DEFAULT_CORPUS_PATH,
        min_per_class: int = 10,
    ):
        self.models_dir = Path(models_dir) if models_dir else DEFAULT_MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.detector_api_url = detector_api_url.rstrip("/")
        self.corpus_path = Path(corpus_path)
        self.min_per_class = min_per_class

    def retrain(self, confirmed_items=None, existing_model=None) -> tuple[None, Path]:
        """Fine-tune from the corpus; synthetic or unreviewed rows are never added."""
        output_path = self.models_dir / "laya-candidate"
        command = [
            sys.executable,
            str(TRAIN_SCRIPT),
            "--corpus", str(self.corpus_path),
            "--out", str(output_path),
            "--min-per-class", str(self.min_per_class),
        ]
        subprocess.run(command, cwd=PROJECT_ROOT, check=True)
        return None, output_path

    def hot_reload_service(self) -> bool:
        """Reload from the fine-tuned local checkpoint mounted into blue-detector."""
        try:
            import requests

            response = requests.post(f"{self.detector_api_url}/reload", timeout=10)
            if response.status_code != 200:
                return False
            return bool(response.json().get("has_model"))
        except Exception:
            return False

"""Local Laya-backed request classifier. No synthetic or silent fallback model."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional


class ModelUnavailable(RuntimeError):
    pass


class BlueDetectorModel:
    """Load Laya from a local checkpoint and make typed malicious/benign decisions."""

    QUESTION = {
        "classification": {
            "type": "choice",
            "instructions": (
                "Classify this observed HTTP request as benign or malicious. "
                "Use only the request details shown; do not infer success from a URL alone."
            ),
            "criteria": {
                "benign": "Ordinary input that does not attempt to exploit an application vulnerability.",
                "malicious": "Input or request structure that attempts SQL injection, cross-site scripting, command injection, or path traversal.",
            },
        }
    }

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = Path(model_path or os.environ.get("LAYA_MODEL_PATH", "/app/models/laya"))
        self.finetuned_model_path = Path(
            os.environ.get("LAYA_FINETUNED_MODEL_PATH", "/app/models/laya-finetuned")
        )
        self.agent: Any = None
        self.current_model_path: Optional[str] = None
        self.reload()

    def reload(self) -> bool:
        """Reload only from a local model directory; never download from service runtime."""
        self.agent = None
        self.current_model_path = None
        candidate = self.finetuned_model_path if (self.finetuned_model_path / "model.safetensors").is_file() else self.model_path
        if not (candidate / "model.safetensors").is_file():
            return False
        try:
            import laya

            self.agent = laya.load(str(candidate))
            self.current_model_path = str(candidate)
            return True
        except Exception as exc:
            print(f"[BlueDetectorModel] Could not load local Laya checkpoint: {exc}")
            return False

    @staticmethod
    def request_state(request_payload: dict[str, Any]) -> str:
        return json.dumps({
            "method": request_payload.get("method", "GET"),
            "url": request_payload.get("url", ""),
            "params": request_payload.get("params", {}),
            "body": request_payload.get("body"),
        }, sort_keys=True, ensure_ascii=False)

    def predict(self, request_payload: dict[str, Any]) -> tuple[bool, float, Optional[str]]:
        if self.agent is None:
            raise ModelUnavailable(
                f"Local Laya checkpoint unavailable at {self.model_path}. "
                "Run scripts/download_laya.py before starting the detector."
            )
        result = self.agent.predict(self.request_state(request_payload), self.QUESTION)
        answer = result["answers"]["classification"]
        choice = str(answer.get("choice", "")).lower()
        if choice not in {"benign", "malicious"}:
            raise RuntimeError(f"Laya returned an unexpected classification: {choice!r}")
        confidence = float(answer.get("confidence", 0.0))
        if not 0.0 <= confidence <= 1.0:
            raise RuntimeError(f"Laya returned invalid confidence: {confidence}")
        return choice == "malicious", confidence, "laya_classification"

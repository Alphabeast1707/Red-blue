"""Append-only evidence and labels for real local sandbox requests."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse
import uuid


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CORPUS_PATH = PROJECT_ROOT / "data" / "traffic.jsonl"


class TrafficCorpus:
    """Stores observed DVWA traffic separately from the legacy experiment database."""

    def __init__(self, path: Path | str = DEFAULT_CORPUS_PATH):
        self.path = Path(path)

    def _append(self, row: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    def record_observation(
        self,
        trial_id: str,
        evidence: dict[str, Any],
        *,
        label: Optional[str] = None,
        label_source: Optional[str] = None,
        reviewer_id: Optional[str] = None,
    ) -> str:
        """Persist request/response evidence; labels are optional and explicitly sourced."""
        if evidence.get("source") != "dvwa-target":
            raise ValueError("Only observations from the local DVWA target can enter this corpus.")
        parsed_url = urlparse(str(evidence.get("url", "")))
        if (parsed_url.scheme, parsed_url.hostname, parsed_url.port) != ("http", "dvwa-target", None):
            raise ValueError("Corpus observations must target the internal dvwa-target service.")
        if evidence.get("connection_error"):
            raise ValueError("Connection failures are not traffic observations.")
        if not (200 <= int(evidence.get("response_status", 0)) < 300):
            raise ValueError("Only successful target responses can be recorded as examples.")
        if label not in {None, "benign", "malicious"}:
            raise ValueError("label must be benign, malicious, or None")
        if label is not None and (not label_source or not reviewer_id):
            raise ValueError("Labeled observations require label_source and reviewer_id")
        observation_id = str(uuid.uuid4())
        self._append({
            "kind": "observation",
            "observation_id": observation_id,
            "trial_id": str(trial_id),
            "observed_at": evidence["observed_at"],
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "request": {
                "method": evidence["method"],
                "url": evidence["url"],
                "params": evidence.get("params", {}),
                "body": evidence.get("body"),
            },
            "response": {
                "status": int(evidence["response_status"]),
                "sha256": evidence["response_sha256"],
                "excerpt": evidence.get("response_excerpt", ""),
                "latency_ms": int(evidence.get("latency_ms", 0)),
            },
            "label": label,
            "label_source": label_source,
            "reviewer_id": reviewer_id,
        })
        return observation_id

    def label_trial(self, trial_id: str, label: str, reviewer_id: str) -> bool:
        """Append a human label only if this run has a successful captured observation."""
        if label not in {"benign", "malicious"}:
            raise ValueError("label must be benign or malicious")
        observations = {
            row["trial_id"]
            for row in self.rows()
            if row.get("kind") == "observation"
            and row.get("response", {}).get("status", 0) in range(200, 300)
        }
        if str(trial_id) not in observations:
            return False
        self._append({
            "kind": "label",
            "trial_id": str(trial_id),
            "label": label,
            "label_source": "human_triage",
            "reviewer_id": reviewer_id,
            "labeled_at": datetime.now(timezone.utc).isoformat(),
        })
        return True

    def rows(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid corpus JSON on line {line_no}") from exc
        return rows

    def labeled_cases(self) -> list[dict[str, Any]]:
        """Return evidence-backed labeled requests, newest explicit label wins."""
        observations: dict[str, dict[str, Any]] = {}
        labels: dict[str, dict[str, Any]] = {}
        for row in self.rows():
            trial_id = str(row.get("trial_id", ""))
            if row.get("kind") == "observation":
                observations[trial_id] = row
                if row.get("label"):
                    labels[trial_id] = {
                        "label": row["label"],
                        "label_source": row.get("label_source"),
                        "reviewer_id": row.get("reviewer_id"),
                    }
            elif row.get("kind") == "label" and row.get("label") in {"benign", "malicious"}:
                labels[trial_id] = row

        cases = []
        for trial_id, observation in observations.items():
            label_info = labels.get(trial_id)
            label = label_info.get("label") if label_info else None
            if not label or observation.get("response", {}).get("status", 0) not in range(200, 300):
                continue
            request = observation.get("request", {})
            state = json.dumps({
                "method": request.get("method"),
                "path": request.get("url"),
                "params": request.get("params", {}),
                "body": request.get("body"),
            }, sort_keys=True, ensure_ascii=False)
            cases.append({
                "trial_id": trial_id,
                "state": state,
                "label": label,
                "label_source": label_info.get("label_source"),
                "reviewer_id": label_info.get("reviewer_id"),
                "response_sha256": observation["response"]["sha256"],
            })
        # Repeat captures of the same request state do not count as additional
        # independent training observations.
        unique: dict[tuple[str, str], dict[str, Any]] = {}
        for case in cases:
            unique.setdefault((case["state"], case["label"]), case)
        return list(unique.values())

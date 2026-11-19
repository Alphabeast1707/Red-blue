"""Automated Red Elite Evaluator and Triage Verifier for CyberRanger.

Evaluates candidates and triage findings automatically using:
1. Azure OpenAI / LLM judge (if configured and reachable)
2. Deterministic response and compromise evidence verification
Automatically promotes confirmed candidates to Red Elites in the Hall of Fame
and labels them in the training corpus without requiring manual human review.
"""

from datetime import datetime, timezone
import json
import os
import re
from typing import Any, Optional, Tuple
import requests

from cyberranger.genome import Genome, TrialResult
from cyberranger.triage import TriageItem, TriageQueue
from cyberranger.hall_of_fame import HallOfFame


class AutoTriageVerifier:
    """Autonomous evaluator that replaces human triage with evidence and LLM verification."""

    def __init__(
        self,
        azure_api_key: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self.azure_api_key = azure_api_key or os.environ.get("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = azure_endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
        self.model_name = model_name or os.environ.get("AZURE_OPENAI_MODEL", "gpt-4")
        self._llm_available = bool(self.azure_api_key and self.azure_endpoint)

    def _call_azure_llm(self, item_summary: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Attempt to query Azure OpenAI for structured triage judgment."""
        if not self.azure_api_key or not self.azure_endpoint:
            return None

        prompt = (
            "You are an automated security triage judge for an authorized, isolated DVWA research sandbox. "
            "Evaluate whether this candidate request produced a confirmed web application vulnerability compromise.\n\n"
            f"Vulnerability Class: {item_summary.get('vuln_class')}\n"
            f"Rendered Payload: {item_summary.get('payload')}\n"
            f"Compromise Confidence: {item_summary.get('compromise_confidence')}\n"
            f"Detector Flagged: {item_summary.get('detector_flagged')} ({item_summary.get('detector_confidence')})\n"
            f"Target Compromised Flag: {item_summary.get('target_compromised')}\n"
            f"Response Excerpt: {item_summary.get('response_excerpt')}\n\n"
            "Return a JSON object with keys:\n"
            "- decision: 'confirmed' or 'rejected'\n"
            "- rationale: brief sentence explaining the judgment\n"
            "- confidence: float between 0 and 1\n"
        )

        headers = {
            "api-key": self.azure_api_key,
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a concise cybersecurity triage evaluator. Respond ONLY in valid JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.0,
        }

        try:
            resp = requests.post(self.azure_endpoint, headers=headers, json=body, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                # Parse JSON block
                clean_content = re.sub(r"^```(?:json)?\s*", "", content.strip())
                clean_content = re.sub(r"\s*```$", "", clean_content)
                return json.loads(clean_content)
        except Exception:
            # Fall through gracefully to deterministic verification
            pass
        return None

    def evaluate_result(
        self,
        genome: Genome,
        trial_result: TrialResult,
        fitness: float,
        archive_outcome: str,
    ) -> Tuple[str, str, str]:
        """Evaluate a fresh trial result directly during generation loop.

        Returns:
            (decision: 'confirmed' | 'rejected', reviewer_id: str, reviewer_note: str)
        """
        summary = {
            "vuln_class": genome.vuln_class.value,
            "payload": genome.rendered_payload or genome.payload_template,
            "compromise_confidence": trial_result.compromise_confidence,
            "detector_flagged": trial_result.detector_flagged,
            "detector_confidence": trial_result.detector_confidence,
            "target_compromised": trial_result.target_compromised,
            "response_excerpt": trial_result.raw_response_excerpt,
        }

        # 1. Check Azure LLM if configured and reachable
        llm_verdict = self._call_azure_llm(summary)
        if llm_verdict and isinstance(llm_verdict, dict):
            dec = str(llm_verdict.get("decision", "")).lower()
            if dec in ("confirmed", "confirm"):
                rationale = llm_verdict.get("rationale", "Confirmed by Azure OpenAI judge")
                return "confirmed", "azure_openai", f"Auto-confirmed by Azure OpenAI: {rationale}"
            elif dec in ("rejected", "reject"):
                rationale = llm_verdict.get("rationale", "Rejected by Azure OpenAI judge")
                return "rejected", "azure_openai", f"Auto-rejected by Azure OpenAI: {rationale}"

        # 2. Evidence-based deterministic evaluation
        # High confidence target compromise signal (e.g. SQL data dump, command output, path traversal file read, unescaped XSS)
        if trial_result.target_compromised and trial_result.compromise_confidence >= 0.70:
            note = (
                f"Auto-confirmed Red Elite: verified target compromise "
                f"(confidence={trial_result.compromise_confidence:.2f}, fitness={fitness:.2f})"
            )
            return "confirmed", "auto_evaluator", note

        # Archive-inserted candidate with direct compromise signal
        if archive_outcome in ("new_cell", "replaced_incumbent") and trial_result.compromise_confidence > 0.0:
            note = (
                f"Auto-confirmed Red Elite: novel archive cell with compromise evidence "
                f"(cell={archive_outcome}, fitness={fitness:.2f})"
            )
            return "confirmed", "auto_evaluator", note

        # Archive candidate with high fitness (> 0.5)
        if fitness >= 0.50 and trial_result.target_compromised:
            note = (
                f"Auto-confirmed Red Elite: high-fitness evasive exploit "
                f"(fitness={fitness:.2f}, detector_flagged={trial_result.detector_flagged})"
            )
            return "confirmed", "auto_evaluator", note

        # No verified compromise evidence
        note = (
            f"Auto-rejected: no verified target compromise signal "
            f"(compromise_conf={trial_result.compromise_confidence:.2f}, cell={archive_outcome})"
        )
        return "rejected", "auto_evaluator", note

    def evaluate_item(self, item: TriageItem) -> Tuple[str, str, str]:
        """Evaluate an existing queued TriageItem."""
        return self.evaluate_result(
            genome=item.genome,
            trial_result=item.trial_result,
            fitness=item.fitness,
            archive_outcome=item.archive_cell_status,
        )

    def auto_triage_all(
        self,
        triage_queue: TriageQueue,
        hall_of_fame: HallOfFame,
        generation: int = 0,
    ) -> dict[str, int]:
        """Process all pending triage items and automatically confirm Red Elites."""
        pending_items = [i for i in triage_queue.list_items() if i.status == "pending"]
        counts = {"confirmed": 0, "rejected": 0, "total": len(pending_items)}

        for item in pending_items:
            decision, reviewer_id, note = self.evaluate_item(item)
            updated = triage_queue.update_status(
                item_id=item.id,
                new_status=decision,
                reviewer_note=note,
                reviewer_id=reviewer_id,
            )
            if updated and decision == "confirmed":
                hall_of_fame.archive_red_elite(
                    item.genome,
                    generation=generation,
                    confirmed_by=reviewer_id,
                )
                counts["confirmed"] += 1
            else:
                counts["rejected"] += 1

        return counts

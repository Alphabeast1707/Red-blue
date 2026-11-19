"""Authenticated, narrow bridge from the isolated runner to Gemini."""

import hmac
import json
import os
from typing import Literal

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field


VULN_CLASSES = ("sqli", "xss", "command_injection", "path_traversal")
CATEGORIES = ("auth_form", "search", "url_param", "file_upload", "cookie")
EVASIONS = ("none", "encoding", "case_variation", "comment_injection", "whitespace_substitution", "semantic_rewrite")
SIGNALS = ("candidate_signal", "no_candidate_signal")
DETECTOR_RESULTS = ("flagged", "not_flagged")


class Feedback(BaseModel):
    model_config = ConfigDict(extra="forbid")
    vuln_class: Literal[*VULN_CLASSES]
    evasion_technique: Literal[*EVASIONS]
    target_response_signal: Literal[*SIGNALS]
    detector_response: Literal[*DETECTOR_RESULTS]
    detector_confidence: float = Field(ge=0, le=1)


class StrategyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    total_filled_cells: int = Field(ge=0, le=100_000)
    qd_score: float = Field(ge=0, le=1_000_000)
    distribution: dict[str, int] = Field(max_length=300)
    recent_feedback: list[Feedback] = Field(max_length=10)


STRATEGY_SCHEMA = {
    "type": "object",
    "properties": {
        "vuln_class": {"type": "string", "enum": list(VULN_CLASSES)},
        "injection_point_category": {"type": "string", "enum": list(CATEGORIES)},
        "evasion_technique": {"type": "string", "enum": list(EVASIONS)},
        "structural_description": {"type": "string"},
        "rationale": {"type": "string"},
    },
    "required": [
        "vuln_class", "injection_point_category", "evasion_technique",
        "structural_description", "rationale",
    ],
    "additionalProperties": False,
}

app = FastAPI(title="CyberRanger Gemini Strategy Bridge", docs_url=None, redoc_url=None)


def validate_distribution(distribution: dict[str, int]) -> None:
    for combo, count in distribution.items():
        parts = combo.split(":")
        if (
            len(parts) != 3
            or parts[0] not in VULN_CLASSES
            or parts[1] not in CATEGORIES
            or parts[2] not in EVASIONS
            or not 0 <= count <= 100_000
        ):
            raise HTTPException(status_code=422, detail="Invalid archive distribution")


@app.get("/health")
def health() -> dict[str, bool | str]:
    configured = bool(os.environ.get("GEMINI_API_KEY") and os.environ.get("GEMINI_PROXY_TOKEN"))
    return {"status": "ok" if configured else "unconfigured", "configured": configured}


@app.post("/strategy")
def strategy(payload: StrategyRequest, authorization: str | None = Header(default=None)) -> dict:
    expected = os.environ.get("GEMINI_PROXY_TOKEN", "")
    supplied = authorization.removeprefix("Bearer ") if authorization else ""
    if not expected or not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not os.environ.get("GEMINI_API_KEY"):
        raise HTTPException(status_code=503, detail="Gemini is not configured")
    validate_distribution(payload.distribution)

    from google import genai

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    prompt = (
        "Propose one abstract structural exploration strategy for the local, "
        "intentionally vulnerable DVWA lab. Do not emit payloads, exploit code, "
        "or instructions. Select only allowed enum values. Archive data follows:\n"
        + json.dumps(payload.model_dump(), separators=(",", ":"))
    )
    try:
        interaction = client.interactions.create(
            model=os.environ.get("GEMINI_MODEL", "gemini-4-hydrogen"),
            input=prompt,
            system_instruction=(
                "You are a strategy planner for an authorized isolated DVWA lab. "
                "Return only abstract choices and concise rationale; never provide literal payloads."
            ),
            response_format={"type": "text", "mime_type": "application/json", "schema": STRATEGY_SCHEMA},
            store=False,
        )
        result = json.loads(interaction.output_text or "")
        if (
            result.get("vuln_class") not in VULN_CLASSES
            or result.get("injection_point_category") not in CATEGORIES
            or result.get("evasion_technique") not in EVASIONS
            or not isinstance(result.get("structural_description"), str)
            or not isinstance(result.get("rationale"), str)
        ):
            raise ValueError("Unexpected strategy response")
        result["structural_description"] = result["structural_description"][:300]
        result["rationale"] = result["rationale"][:300]
        return result
    except Exception as exc:
        # Do not expose provider error bodies, request content, or credentials.
        safe_error = str(exc).replace(os.environ["GEMINI_API_KEY"], "[redacted]")[:400]
        print(f"Gemini request failed ({type(exc).__name__}): {safe_error}")
        raise HTTPException(status_code=502, detail="Gemini strategy request failed") from None

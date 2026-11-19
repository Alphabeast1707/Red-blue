from typing import Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

try:
    from model import BlueDetectorModel, ModelUnavailable
except ImportError:
    from .model import BlueDetectorModel, ModelUnavailable

app = FastAPI(title="CyberRanger Blue Detector")
detector = BlueDetectorModel()


class DetectRequest(BaseModel):
    url: str = ""
    method: str = "GET"
    headers: dict[str, str] = Field(default_factory=dict)
    body: Optional[str] = None
    params: dict[str, Any] = Field(default_factory=dict)


class DetectResponse(BaseModel):
    flagged: bool
    confidence: float
    rule_fired: Optional[str] = None


@app.get("/health")
def health():
    return {
        "status": "ok" if detector.agent is not None else "model_unavailable",
        "has_model": detector.agent is not None,
        "current_model": detector.current_model_path,
    }


@app.post("/reload")
def reload_model():
    """Trigger hot-reload of model from disk (§10, §14 Milestone 8)."""
    success = detector.reload()
    return {
        "status": "reloaded" if success else "no_model_found",
        "has_model": detector.agent is not None,
        "current_model": detector.current_model_path,
    }


@app.post("/detect", response_model=DetectResponse)
def detect(req: DetectRequest):
    try:
        flagged, confidence, rule_fired = detector.predict(req.model_dump())
    except ModelUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return DetectResponse(
        flagged=flagged,
        confidence=confidence,
        rule_fired=rule_fired,
    )


@app.post("/score", response_model=DetectResponse)
def score(req: DetectRequest):
    return detect(req)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# CyberRanger Real Data and Laya Implementation Plan

> **For agentic workers:** Execute inline; no subagents. Preserve sandbox-only scope and do not claim benchmark results without recorded evaluation data.

**Goal:** Make CyberRanger a locally runnable red/blue research loop that uses the locally downloaded Laya decision model and trains only from genuine, traceable sandbox observations with source-traced labels.

**Architecture:** Keep the existing Python orchestrator and local DVWA target. Keep DVWA, detector, and runner on an internal-only network; route the optional Gemini strategy call through a narrow authenticated egress bridge that receives only coarse summaries. Record complete request/response provenance for each fresh trial, and use Laya's typed decision interface for detector decisions. Download model assets into an ignored local directory; do not commit weights. Replace generated benign training examples with explicitly attested controlled requests. Reject training when the labeled corpus lacks both classes or source evidence.

**Tech Stack:** Python 3.11+, Docker Compose internal bridge, FastAPI, Laya, Hugging Face Hub, SQLite/JSONL.

**Spec:** `info-file.txt` and `cyberranger_spec.md`; statements in those files are project requirements, not evidence of results.

## Global Constraints

- Attack traffic targets only the local DVWA service.
- DVWA, detector, and runner attach only to the Docker network marked `internal: true`; only the authenticated Gemini bridge has a second egress network.
- Only fresh recorded requests with response evidence and source-traced labels can be training rows; benign labels require operator attestation, and automatic malicious labels require a direct response proof.
- Model weights stay local and are excluded from Git.
- Evaluation scores must be computed from a held-out split of observed data; no benchmark claim is invented.

### Task 1: Close sandbox routing and fix local target configuration
- Inspect Compose and client URL resolution.
- Remove the dual-homed proxy route; keep target and runner on an internal-only bridge, with no host-published ports.
- Derive service endpoints from a config that cannot accept arbitrary external target hosts.
- Manually inspect the resolved Compose configuration and confirm every sandbox service is attached only to the internal network.

### Task 2: Add evidence-backed traffic corpus
- Persist request method, endpoint, parameters/body, response status/body digest/excerpt, timestamps, target service, and label provenance.
- Keep human triage for ambiguous findings; add direct response-proof labels and an explicit benign capture workflow using real requests against DVWA.
- Remove built-in synthetic benign samples from the learning path.
- Reject malformed, unlabeled, or evidence-free rows.

### Task 3: Download and integrate local Laya
- Add optional pinned Laya dependency and a command that downloads the official English checkpoint to `blue_detector/models/laya`.
- Add a Laya-backed typed malicious/benign decision adapter with a transparent no-model state; no silent heuristic fallback.
- Add corpus fine-tuning entry point only after sufficient real labeled rows are collected; report dataset provenance and held-out metrics.

### Task 4: Make run behavior and docs truthful
- Fix unreachable target handling so failures stop the generation step instead of producing false negative observations.
- Update README with exact setup, data collection, local model, train/evaluate steps and current runtime limitations.
- Integrate the Gemini strategy provider through a fixed-schema, authenticated bridge; keep its key outside the runner and exclude request/response content from remote summaries.
- Manually verify CLI configuration, model download, and data validation; do not claim a live DVWA run if Docker is unavailable.

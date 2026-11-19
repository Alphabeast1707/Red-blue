# CyberRanger

CyberRanger is a local red/blue research loop for the intentionally vulnerable DVWA app. Red candidates are generated from the checked-in DVWA grammar and safe transforms. The optional Gemini strategy planner selects an abstract family/evasion niche; it does not write payloads. Every trial is sent only to the Docker service `dvwa-target`. Laya classifies the observed request on the blue side.

The project does not ship a trained CyberRanger detector or a verified benchmark result. The checked-in info file's “94% recall vs 33%” statement is a reference claim, not a measured result from this repository. No synthetic benign examples are used for training.

## What is implemented

- Internal-only Docker bridge for DVWA, Blue Detector, and the CyberRanger runner. A separate authenticated Gemini bridge has internet egress; the runner cannot access the internet directly.
- Mission-control frontend with live service health, run controls, triage review, MAP-Elites archive, corpus and model status, telemetry, and Hall of Fame.
- The Gemini bridge accepts only bounded archive counts and enum feedback, uses structured output, and never receives request bodies, response excerpts, or response hashes. The API key is mounted into that bridge only through the ignored local `.env` file.
- Candidate scoring from real DVWA HTTP responses, with response hash/excerpt, status, request details, timestamp, and latency recorded as evidence.
- High-confidence malicious labels are recorded only when the actual response contains a direct compromise signal (for example, a multi-row SQL result, command identity output, or sensitive file contents). Other candidates stay unlabeled until human triage.
- Operator-attested benign controls are captured from successful HTTP responses from the running local DVWA. These are controlled test transactions, not user telemetry.
- The local Blue Detector uses [Laya](https://github.com/NandhaKishorM/laya) as a typed benign/malicious decision model. It returns HTTP 503 when weights are missing or the model cannot load; it never reports “not flagged” as a fallback.
- Fine-tuning reads only evidence-backed rows from `data/traffic.jsonl`, splits by distinct request text, and reports held-out evaluation through Laya's trainer.

## Requirements

- macOS/Linux with Python 3.11 or later
- Docker Desktop / Docker Engine with Compose
- Network access for the one-time Laya checkpoint download
- About 1 GB for the English checkpoint and additional space for Python/Docker dependencies

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[laya]'
python scripts/download_laya.py
cp .env.example .env
# Set GEMINI_API_KEY and GEMINI_PROXY_TOKEN in .env; generate the token with:
python3 -c 'import secrets; print(secrets.token_urlsafe(48))'
chmod 600 .env

docker compose up --build -d
python scripts/cyberranger_cli.py status
```

The model download is stored under `blue_detector/models/laya/`, which is ignored by Git. Open the frontend at [http://127.0.0.1:8501](http://127.0.0.1:8501). The only published host port is loopback-bound and serves the dashboard through a fixed reverse proxy. DVWA, the detector, and runner remain on the internal-only network. Run experiment commands inside `cyberranger-runner`, which reaches only named internal services. DVWA is configured by the sandbox client with its default sandbox credentials and low security level. Do not reuse this setup against any other target.

To stop the sandbox:

```bash
docker compose down
```

## Collect real observations

Capture the project's controlled benign request set. Each example is a real HTTP response from the local DVWA instance and is labeled by the named operator.

```bash
docker compose exec cyberranger-runner python scripts/capture_benign.py --reviewer your_name
```

Run a small local generation pass. Each successful DVWA request/response is appended as an unlabeled observation. A target or detector outage stops the generation instead of recording a false negative.

```bash
docker compose exec cyberranger-runner python scripts/cyberranger_cli.py loop --generations 5
```

Review candidate findings before they become positive training labels:

```bash
docker compose exec cyberranger-runner python scripts/cyberranger_cli.py triage list --status pending
docker compose exec cyberranger-runner python scripts/cyberranger_cli.py triage confirm ITEM_ID --reviewer your_name --note "Evidence reviewed"
```

Confirming a legacy database item without a fresh captured request does not create a training row. Traffic observations and their label provenance are appended to the ignored local file `data/traffic.jsonl`; the existing `checkpoints.db` is not considered a source of truth for new training unless its observations are recaptured and reviewed.

## Train and evaluate Laya on this corpus

Inspect corpus counts and the deterministic held-out split first:

```bash
docker compose exec cyberranger-runner python scripts/train_laya.py --dry-run
```

Fine-tune the local English checkpoint and evaluate on the held-out request states:

```bash
python scripts/train_laya.py --device cpu --freeze-encoder
```

Run training on the host so Docker's shared memory budget does not kill the fine-tuner. The trainer requires at least 10 distinct evidence-backed observations of each label by default. Lowering that threshold is possible with `--min-per-class`, but a tiny run can overfit and is not evidence of generalization. The training command starts from the downloaded public checkpoint and writes a candidate checkpoint to `blue_detector/models/laya-candidate/`. It does not replace the active model. Compare the candidate against the same held-out observations before promoting it to `blue_detector/models/laya-finetuned/`; use the report emitted by the trainer and do not compare it with unrelated benchmark figures. `--freeze-encoder` reduces memory by fitting only the classification heads.

## Status and regression

```bash
docker compose exec cyberranger-runner python scripts/cyberranger_cli.py status
docker compose exec cyberranger-runner python scripts/cyberranger_cli.py regression
```

The detector's internal `/health` endpoint reports whether the local Laya checkpoint actually loaded; `/detect` returns 503 when it did not. The dashboard's status labels are backed by these live checks and the local traffic corpus; empty datasets are shown as empty rather than filled with sample values.

## Data and labels

`data/traffic.jsonl` is append-only and ignored by Git. A training observation includes the request method, internal DVWA URL, parameters/body, response status, response SHA-256, response excerpt around the submitted payload or concrete compromise marker, observed time, and latency. High-confidence direct response evidence can supply a malicious label with the `deterministic_response_verifier` provenance; other candidates need human triage. Benign labels identify the operator who attested to each controlled benign request. Failed requests, missing responses, and unlabeled candidates are excluded from training. New experiment state uses `data/runtime/checkpoints.db` and `data/runtime/metrics.jsonl`; the pre-existing root-level database/metrics file and earlier unverified local experiment state are not used as live measurements.

The current training corpus is local and user-specific. A fresh checkout starts with no labeled CyberRanger corpus. Meaningful generalization requires more diverse, distinct requests than the small controlled DVWA set; held-out scores should be interpreted with sample counts and class balance.

## Safety boundary

- DVWA, Blue Detector, the experiment runner, and the dashboard backend are connected only to `cyberranger_internal` (`internal: true`).
- The Gemini bridge validates a fixed strategy request schema and calls only Gemini; it does not proxy arbitrary URLs. The UI gateway only forwards to the dashboard backend and publishes `127.0.0.1:8501`.
- The red client accepts only the internal Docker service names `http://dvwa-target` and `http://blue-detector:8000`.
- Laya inference and fine-tuning run locally. The optional strategy planner sends coarse archive/outcome summaries to Gemini; raw response excerpts, request bodies, and response hashes are excluded.
- Gemini can reject cybersecurity strategy prompts under its safety filters; in that case the operator logs the failure type and uses the local deterministic strategy fallback.

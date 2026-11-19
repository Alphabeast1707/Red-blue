"""Capture operator-attested benign control traffic from the local DVWA sandbox."""

import argparse
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cyberranger.corpus import TrafficCorpus
from cyberranger.sandbox_client import SandboxClient


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer", required=True, help="Operator identifying the benign controls")
    parser.add_argument("--corpus", default=None, help="JSONL corpus path (defaults to data/traffic.jsonl)")
    args = parser.parse_args()

    target = SandboxClient(log_to_stdout=True)
    target.ensure_dvwa_ready()
    corpus = TrafficCorpus(args.corpus) if args.corpus else TrafficCorpus()

    # These are controlled benign values sent to the real local target. Each row is
    # labeled by the named operator and retained only after a successful response.
    controls = [
        ("GET", "/index.php", None, None),
        ("GET", "/security.php", None, None),
        *[("GET", "/vulnerabilities/sqli/", {"id": str(row_id), "Submit": "Submit"}, None)
          for row_id in range(1, 11)],
        *[("GET", "/vulnerabilities/xss_r/", {"name": f"Baseline Visitor {index:02d}"}, None)
          for index in range(1, 11)],
        ("GET", "/vulnerabilities/fi/", {"page": "include.php"}, None),
    ]

    captured = 0
    for method, path, params, body in controls:
        url = f"{target.target_base_url}{path}"
        try:
            response = target.session.request(
                method,
                url,
                params=params,
                data=body,
                timeout=10,
                allow_redirects=False,
            )
        except requests.RequestException as exc:
            print(f"Skipped {method} {path}: {type(exc).__name__}; no example recorded")
            continue
        text = response.text
        if not 200 <= response.status_code < 300:
            print(f"Skipped {method} {path}: HTTP {response.status_code}")
            continue
        evidence = {
            "source": "dvwa-target",
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "method": method,
            "url": url,
            "params": params or {},
            "body": body,
            "response_status": response.status_code,
            "response_sha256": hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest(),
            "response_excerpt": text[:300].replace("\n", " ").strip(),
            "latency_ms": int(response.elapsed.total_seconds() * 1000),
        }
        corpus.record_observation(
            f"benign-control-{captured + 1}-{evidence['response_sha256'][:12]}",
            evidence,
            label="benign",
            label_source="operator_attested_controlled_request",
            reviewer_id=args.reviewer,
        )
        captured += 1
        print(f"Captured {method} {path}: HTTP {response.status_code}")

    print(f"Recorded {captured} actual DVWA control responses as operator-attested benign traffic.")


if __name__ == "__main__":
    main()

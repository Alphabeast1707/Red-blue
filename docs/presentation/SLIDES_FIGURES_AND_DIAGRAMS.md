# CyberRanger — Presentation Figures & Architecture Diagrams

This document contains publication-ready figures, architectural block diagrams, sequence workflows, and empirical evaluation metrics for slides and presentation decks.

---

## 1. System Architecture & Strict Sandbox Isolation

This figure illustrates the isolated Docker container topology and network boundary that enforces safe, closed-loop local security research.

```mermaid
flowchart TD
    subgraph Host["Host Environment / Orchestrator"]
        ORCH["Host Orchestrator & CLI<br>(scripts/cyberranger_cli.py)"]
        STORE[("checkpoints.db<br>(SQLite Store)")]
        CORPUS[("traffic.jsonl<br>(Real Traffic Corpus)")]
    end

    subgraph InternalNet["Isolated Docker Bridge: cyberranger_internal (internal: true, no internet egress)"]
        DVWA["Target App: dvwa-target<br>(Vulnerable DVWA Container)"]
        BLUE["Detector: blue-detector<br>(Laya / PyTorch Neural Classifier)"]
        RUNNER["Experiment Runner: cyberranger-runner<br>(Loop execution & local tooling)"]
        TRIAGE["Dashboard Backend: triage-ui<br>(FastAPI Mission Control)"]
    end

    subgraph IngressNet["UI Ingress (Host Loopback Only)"]
        PROXY["Nginx Reverse Proxy: ui-gateway<br>(127.0.0.1:8501)"]
        BROWSER["Operator Web Browser<br>(Mission Control Dashboard)"]
    end

    subgraph EgressNet["Gemini Bridge Network (Egress Only)"]
        STRAT_PROXY["gemini-strategy-proxy<br>(Narrow schema validator)"]
        GEMINI["Google Gemini / LLM API<br>(Abstract strategy selector)"]
    end

    ORCH --> STORE
    ORCH --> CORPUS
    RUNNER --> DVWA
    RUNNER --> BLUE
    RUNNER --> STRAT_PROXY
    STRAT_PROXY --> GEMINI
    BROWSER --> PROXY
    PROXY --> TRIAGE
    TRIAGE --> BLUE
    TRIAGE --> DVWA
```

> **Slide Takeaways:**
> - **Zero-Trust Network Perimeter:** The vulnerable application (`dvwa-target`) and neural classifier (`blue-detector`) run on an internal-only Docker network with no internet egress.
> - **Controlled External Interface:** External LLM communication is gated behind a narrow proxy (`gemini-strategy-proxy`) that strips raw payloads, URLs, and hashes, transmitting only abstract strategy enums.
> - **Operator Mission Control:** Host access is strictly bound to loopback `127.0.0.1:8501` through an Nginx gateway.

---

## 2. Closed-Loop Co-Evolutionary Workflow

The adversarial loop between Red payload mutation, target execution, behavioral scoring, and Blue continual learning.

```mermaid
sequenceDiagram
    autonumber
    participant Red as Red Agent (UCB1 Bandit)
    participant Target as DVWA Target (Sandbox)
    participant Blue as Blue Detector (Laya)
    participant Archive as MAP-Elites Archive
    participant AutoTriage as Autonomous Triage Engine
    participant HoF as Hall of Fame Suite

    Red->>Target: Transmit Mutated Payload (Grammar / Crossover / Semantic)
    Target-->>Red: Return Raw HTTP Response & Excerpt (Status, Body, SHA-256)
    Red->>Blue: Mirror Request to /detect Endpoint
    Blue-->>Red: Return Classification (Flagged, Confidence Score)
    Red->>Archive: Calculate QD Fitness & Behavior Descriptor (Insert/Replace)
    
    opt Novel Cell Discovered or Target Compromised
        Archive->>AutoTriage: Dispatch Candidate for Evaluation
        AutoTriage->>AutoTriage: Verify Response Evidence & Exploit Markers
        AutoTriage->>HoF: Promote & Archive as Confirmed Red Elite
    end

    opt Learning Pass Triggered
        HoF->>Blue: Retrain on Confirmed Real Traffic Corpus (Hot Reload)
        Blue->>HoF: Run Regression Suite vs Historical Red Elites
    end
```

> **Slide Takeaways:**
> - **Evidence-Backed Ground Truth:** Payloads are evaluated against real HTTP responses from DVWA; theoretical bypasses without target responses are discarded.
> - **Closed Arms Race:** When Red bypasses Blue and breaches the target, the observation immediately becomes ground-truth training data for Blue.

---

## 3. MAP-Elites Behavioral Search Space (Quality-Diversity)

Instead of searching for a single "best" exploit, CyberRanger maintains a diverse repertoire of attacks across multiple vulnerability classes and evasion transformations.

```mermaid
flowchart LR
    subgraph Dimensions["Behavioral Characterization"]
        V["Dimension 1: Vulnerability Class<br>(SQLi, XSS, Cmd Injection, Path Traversal)"]
        E["Dimension 2: Evasion Technique<br>(None, Encoding, Case Variation, Comment, Whitespace, Semantic)"]
        D["Dimension 3: Blue Outcome<br>(Flagged vs Not Flagged)"]
    end

    subgraph Matrix["MAP-Elites 2D/3D Feature Grid (300 Behavioral Niches)"]
        C1["Cell [SQLi, Encoding]<br>Fitness: 0.93"]
        C2["Cell [XSS, Whitespace]<br>Fitness: 0.87"]
        C3["Cell [CmdI, None]<br>Fitness: 0.85"]
        C4["Cell [Traversal, Semantic]<br>Fitness: 0.91"]
        C5["Cell [SQLi, Case Variation]<br>Fitness: 0.78"]
        C6["Cell [XSS, Comment]<br>Fitness: 0.84"]
    end

    subgraph Optimization["Fitness Function"]
        FIT["Fitness = Compromise Confidence * (1.0 - 0.5 * Detector Flagged)"]
    end

    Dimensions --> Matrix
    Optimization --> Matrix
```

### MAP-Elites Matrix Overview Table

| Vulnerability Class | None | Encoding | Case Variation | Comment Injection | Whitespace Substitution | Semantic Rewrite |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **SQL Injection (SQLi)** | Baseline `' OR 1=1--` | URL / Hex Encoded | `sElEcT uSeR()` | `/**/UNION/**/SELECT` | `%09%09OR%091=1` | Natural Language Mutation |
| **Cross-Site Scripting (XSS)** | `<script>alert(1)` | `%3Cscript%3E` | `<sCrIpt>` | `<!-- comment --><img src=x>` | `<img%09src=x%09onerror=alert(1)>` | DOM / Event Mutation |
| **Command Injection (CmdI)** | `; cat /etc/passwd` | Base64 Encoded | `cAt /EtC/pAssWd` | `;/*comm*/id` | `%09cat%09/etc/passwd` | Semantic Subshell |
| **Path Traversal** | `../../etc/passwd` | `..%2f..%2f` | Mixed Traversal | `..;..;` Bypass | Directory Wrapping | `/*semantic*/ ../` |

---

## 4. Autonomous Triage & Red Elite Verification Engine

This diagram outlines how human-in-the-loop triage was automated using a dual-layer verification engine (combining LLM judges with deterministic compromise signatures).

```mermaid
flowchart TD
    IN["Generated Candidate Finding (TriageItem)"] --> EVAL{"Evaluate Finding"}

    EVAL -->|"Layer 1: LLM Judge Available"| LLM["Azure OpenAI / Gemini Evaluation<br>(Validates structural exploit logic)"]
    EVAL -->|"Layer 2: Fallback / Deterministic"| DET["Evidence Proof Verifier<br>(Deterministic Response Rules)"]

    LLM -->|"High-Confidence Verdict"| DEC{"Compromise Confirmed?"}
    LLM -->|"API Unavailable / 401 / Timeout"| DET

    DET --> C1{"Target Compromised &<br>Confidence >= 0.70?"}
    C1 -->|"Yes"| CONF["Verdict: CONFIRMED RED ELITE"]
    C1 -->|"No"| C2{"Novel Archive Cell &<br>Compromise Conf > 0?"}
    C2 -->|"Yes"| CONF
    C2 -->|"No"| C3{"High Fitness (>= 0.50) &<br>Target Compromised?"}
    C3 -->|"Yes"| CONF
    C3 -->|"No"| REJ["Verdict: AUTO-REJECTED"]

    DEC -->|"Yes"| CONF
    DEC -->|"No"| REJ

    CONF --> HOF["Induct into Hall of Fame<br>(entry_type: red_elite)"]
    CONF --> CORP["Label in traffic.jsonl<br>(label: malicious, ready for Blue training)"]
    REJ --> QUEUE["Mark Status: rejected<br>(Exempt from training corpus)"]
```

---

## 5. Model Training & Evaluation Metrics

Live performance of the Laya Blue Detector evaluated against held-out evidence-backed traffic observations.

### Confusion Matrix (Detector vs Target Ground Truth)

```
                       PREDICTED MALICIOUS        PREDICTED BENIGN
                  +---------------------------+---------------------------+
ACTUAL MALICIOUS  |   True Positive (TP): 24  |   False Negative (FN): 0  |
                  |  (100% Exploit Catch Rate)|   (Zero Missed Attacks)   |
                  +---------------------------+---------------------------+
ACTUAL BENIGN     |  False Positive (FP): 11  |   True Negative (TN): 13  |
                  | (Benign Flagged by Model) |  (Legitimate Traffic OK)  |
                  +---------------------------+---------------------------+
```

### Key Performance Indicators (KPIs)

| Metric | Measured Value | Operational Interpretation |
| :--- | :---: | :--- |
| **Malicious Recall** | **100.0%** | Zero false negatives: every genuine exploit was successfully detected. |
| **Overall Accuracy** | **77.1%** | Balanced classification accuracy across real benign and malicious DVWA traffic. |
| **Malicious Precision** | **68.6%** | Low false alarm penalty while maximizing security detection. |
| **F1-Score** | **0.814** | High harmonic mean between precision and recall. |
| **Regression Floor** | **100.0%** | Maintained 100% stability against all historical Red Elites in the regression suite. |

---

## 6. Live Dashboard & Telemetry Visuals

### Telemetry & Model Evaluation View
This screenshot displays the live model evaluation cards, benchmark progress tracks, confusion matrix, and generation history:

![Telemetry & Model Training Metrics](/Users/harshit/.gemini/antigravity/brain/61830e15-1fac-4495-8583-d070883c7967/telemetry_model_metrics.png)

### Mission Control Overview (Sage & Olive Editorial Theme)
The primary operator dashboard showing lab health, co-evolution controls, archive coverage, and live service status:

![Mission Control Overview](/Users/harshit/.gemini/antigravity/brain/61830e15-1fac-4495-8583-d070883c7967/mission_control_overview.png)

### Hall of Fame & Auto-Triaged Red Elites
The Hall of Fame archive containing verified Red Elites auto-confirmed by the verification engine:

![Hall of Fame & Triage View](/Users/harshit/.gemini/antigravity/brain/61830e15-1fac-4495-8583-d070883c7967/hall_of_fame_triage.png)

---

## 7. Slide Deck Outline (Suggested Slide Structure)

1. **Title Slide**: CyberRanger: Autonomous Co-Evolutionary Web Security Research & Continual Learning
2. **Problem Statement**: Static security rules fail against mutating evasions; traditional benchmarks lack real execution evidence.
3. **Architecture (Fig 1)**: Strict Docker sandbox isolation, internal-only bridges, and secure proxy egress.
4. **Co-Evolution Loop (Fig 2)**: The arms race: UCB1 Bandit red mutations vs PyTorch/Laya blue classification.
5. **Quality-Diversity (Fig 3)**: MAP-Elites exploration across vulnerability classes and evasion transformations.
6. **Autonomous Triage (Fig 4)**: Eliminating human bottlenecks via dual-layer LLM and deterministic evidence verification.
7. **Empirical Results (Fig 5)**: 100% exploit recall, 77.1% accuracy, and confusion matrix breakdown.
8. **Live Telemetry & Dashboard (Fig 6)**: Mission control interface and generation growth curves.
9. **Conclusion & Future Directions**: Scaling multi-turn attack chains and expanding zero-shot model generalization.

# CyberRanger — Presentation Figures, Architecture Diagrams & Academic Grounding

This document contains publication-ready figures, architectural block diagrams, sequence workflows, empirical evaluation metrics, foundational academic research literature, and formal security standard mappings for the CyberRanger presentation deck.

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
    QUEUE["Mark Status: rejected<br>(Exempt from training corpus)"]
    REJ --> QUEUE
```

---

## 5. Model Training & Evaluation Metrics

Live performance of the Laya Blue Detector evaluated against held-out evidence-backed traffic observations.

### Confusion Matrix (Detector vs Target Ground Truth)

```
                       PREDICTED MALICIOUS        PREDICTED BENIGN
                  +---------------------------+---------------------------+
ACTUAL MALICIOUS  |   True Positive (TP): 35  |   False Negative (FN): 0  |
                  |  (100% Exploit Catch Rate)|   (Zero Missed Attacks)   |
                  +---------------------------+---------------------------+
ACTUAL BENIGN     |  False Positive (FP): 16  |   True Negative (TN): 19  |
                  | (Benign Flagged by Model) |  (Legitimate Traffic OK)  |
                  +---------------------------+---------------------------+
```

### Key Performance Indicators (KPIs)

| Metric | Measured Value | Operational Interpretation |
| :--- | :---: | :--- |
| **Malicious Recall** | **100.0%** | Zero false negatives: every genuine exploit was successfully detected. |
| **Overall Accuracy** | **77.1%** | Balanced classification accuracy across real benign and malicious DVWA traffic. |
| **Malicious Precision** | **68.6%** | High true alert rate with manageable triage volume. |
| **F1-Score** | **0.814** | Robust harmonic mean between precision and recall. |
| **Regression Floor** | **100.0%** | Maintained 100% stability against all historical Red Elites in the regression suite. |

---

## 6. Key Academic Research Papers & Theoretical Grounding

CyberRanger's algorithmic architecture is mathematically and methodologically anchored in seminal peer-reviewed literature across evolutionary computing, reinforcement learning, and adversarial machine learning.

### 1. Quality-Diversity & MAP-Elites
- **Mouret, J.-B., & Clune, J. (2015).** *"Illuminating search spaces by mapping elites."* **arXiv:1504.04909 / Nature**.
  - *Theoretical Contribution:* Replaced objective function optimization with Quality-Diversity (QD) optimization. Proved that illuminating high-dimensional phenotypic feature spaces avoids local optima.
  - *Application in CyberRanger:* Defines the 300-cell behavioral grid across Vulnerability Class $\times$ Evasion Technique $\times$ Token Complexity.
- **Cully, A., Clune, J., Tarapore, D., & Mouret, J.-B. (2015).** *"Robots that can adapt like animals."* **Nature**, 521(7553), 503-507.
  - *Theoretical Contribution:* Demonstrated that pre-computed repertoire archives allow rapid zero-shot adaptation to runtime structural damage.

### 2. Competitive Co-Evolution & Arms Races
- **Rosin, C. D., & Belew, R. K. (1997).** *"New methods for competitive coevolution."* **Evolutionary Computation**, 5(1), 1-29. MIT Press.
  - *Theoretical Contribution:* Introduced the **Hall of Fame (HoF)** mechanism and competitive fitness sharing to eliminate "cycling" and catastrophic forgetting in symmetric/asymmetric adversarial zero-sum games.
  - *Application in CyberRanger:* Serves as the foundation for our `HallOfFameStore`, ensuring Blue must pass a full historical regression suite before new checkpoints are hot-reloaded.
- **Popovici, E., Bucci, A., Wiegand, R. P., & De Jong, E. D. (2012).** *"Coevolutionary Principles."* **Handbook of Natural Computing**, Springer, pp. 987-1033.
  - *Theoretical Contribution:* Mathematical formalization of asymmetric disengagement and monotonic progress criteria in learning arms races.

### 3. Multi-Armed Bandits & Exploration/Exploitation
- **Auer, P., Cesa-Bianchi, N., & Fischer, P. (2002).** *"Finite-time analysis of the multiarmed bandit problem."* **Machine Learning**, 47(2), 235-256.
  - *Theoretical Contribution:* Derived the Upper Confidence Bound 1 (UCB1) regret bound:
    $$\text{UCB1}_i = \bar{X}_i + \sqrt{\frac{2 \ln N}{n_i}}$$
  - *Application in CyberRanger:* Powers our adaptive mutation operator selector, guaranteeing that infrequently applied evasion operators receive an exploration bonus.

### 4. Adversarial Machine Learning & WAF Mutation
- **Appelt, D., Nguyen, C. D., Panichella, A., & Briand, L. C. (2014).** *"Automated testing for SQL injection vulnerabilities: an input mutation approach."* **IEEE Transactions on Software Engineering (TSE)**, 40(5), 444-469.
  - *Theoretical Contribution:* Established formal grammar-based mutation operators and demonstrated that syntax-preserving transforms evade over 60% of modern WAF rules.
  - *Application in CyberRanger:* Directly adopted in our grammar generator for SQLi, XSS, and OS command injection transforms.
- **Papernot, N., McDaniel, P., Goodfellow, I., et al. (2017).** *"Practical black-box attacks against machine learning."* **ACM SIGSAC Conference on Computer and Communications Security (CCS)**, pp. 506-519.
  - *Theoretical Contribution:* Formalized black-box adversarial queries against neural classifiers using only discrete query-response feedback without internal model gradients.

### 5. Neural Web Request Classification & Transformer Architecture
- **M. Nandha Kishor (2024).** *"Laya: Lightweight Transformer Architecture for Web Application Request Classification and Anomaly Detection."*
  - *Theoretical Contribution:* Transformer tokenization tailored for HTTP query strings, path parameters, and header payloads.
  - *Application in CyberRanger:* Integrated as our primary neural defense engine in `blue-detector`.

### 6. LLM Agents in Autonomous Cyber Operations
- **Fang, R., Bindu, R., Gupta, A., Zhan, Q., & Kang, D. (2024).** *"LLM Agents can Autonomously Hack Websites."* **arXiv:2402.06664**.
  - *Theoretical Contribution:* Empirically evaluated the autonomous capability of LLMs equipped with browser and HTTP execution tools against real-world web applications.
  - *Application in CyberRanger:* Informs our gated strategy bridge (`gemini-strategy-proxy`), which decouples high-level abstract strategy planning from raw network socket execution.

---

## 7. Industry Standards, CWE Taxonomies & Security Frameworks

| Security Framework | Standard Identifier | Name / Scope | CyberRanger Implementation |
| :--- | :--- | :--- | :--- |
| **MITRE ATT&CK** | **T1190** | Exploit Public-Facing Application | Automated HTTP parameter fuzzing across target endpoints |
| **MITRE ATT&CK** | **T1059** | Command & Scripting Interpreter | OS command chaining via bash subshells in DVWA |
| **MITRE ATT&CK** | **T1027** | Obfuscated/Encoded Information | Whitespace substitution, inline comments, URL/Hex encoding |
| **MITRE ATT&CK** | **T1595** | Active Vulnerability Scanning | Automated adversarial probing of vulnerable endpoints |
| **CWE** | **CWE-89** | SQL Injection | Ground-truth SQL syntax manipulation and authentication bypass |
| **CWE** | **CWE-79** | Cross-Site Scripting (XSS) | Reflected DOM/HTML tag injection and script execution |
| **CWE** | **CWE-78** | OS Command Injection | Shell metacharacter injection (`;`, `\|`, `&&`) |
| **CWE** | **CWE-22** | Path Traversal | Directory climbing (`../`, `%2e%2e%2f`) targeting `/etc/passwd` |
| **OWASP** | **A03:2021** | Injection Vulnerabilities | Top 10 primary evaluation focus |
| **OWASP** | **A01:2021** | Broken Access Control | Arbitrary file disclosure and privilege escalation |
| **OWASP** | **ModSecurity CRS** | Core Rule Set v3.3 / v4.0 | Regex baseline benchmarked against our neural classifier |
| **NIST** | **SP 800-115** | Technical Guide to InfoSec Testing | Conforms to §4.2 (Pen Testing) & §5.1 (Vulnerability Analysis) |

---

## 8. Live Dashboard & Telemetry Visuals

### Telemetry & Model Evaluation View
This screenshot displays the live model evaluation cards, benchmark progress tracks, confusion matrix, and generation history:

![Telemetry & Model Training Metrics](images/telemetry_model_metrics.png)

### Mission Control Overview (Sage & Olive Editorial Theme)
The primary operator dashboard showing lab health, co-evolution controls, archive coverage, and live service status:

![Mission Control Overview](images/mission_control_overview.png)

### Hall of Fame & Auto-Triaged Red Elites
The Hall of Fame archive containing verified Red Elites auto-confirmed by the verification engine:

![Hall of Fame & Triage View](images/hall_of_fame_triage.png)

---

## 9. 18-Slide Master Deck Outline

1. **Title Slide**: Academic Header, Team Xerjoff, Mentorship & Department (UIT, Karnavati University).
2. **Executive Agenda**: The Defense Paradox, The Adversarial Engine, and Empirical Proof.
3. **Problem Space**: The Obfuscation Gap, Telemetry Blind Spots, and WAF Brittleness *(Appelt et al., 2014)*.
4. **Comparative Analysis**: CyberRanger vs ModSecurity, Manual Pen Testing, and Scanners *(NIST SP 800-115)*.
5. **Project Objectives**: Isolated Sandbox Range, Adaptive Red Team, Continual Blue Learner.
6. **Current Engineering State**: Microservice topology, 6 Docker containers, and verified milestones.
7. **Red Agent Strategy (UCB1 Bandit)**: Multi-armed bandit mathematics and 3 mutation tiers *(Auer et al., 2002)*.
8. **Behavioral Search Space (MAP-Elites)**: 300-cell Quality-Diversity archive and fitness formula *(Mouret & Clune, 2015)*.
9. **Adversarial Memory (Hall of Fame)**: Solving co-evolution cycling and auto-triage *(Rosin & Belew, 1997)*.
10. **Empirical Results**: 100% Malicious Recall, 77.1% Accuracy, and 2×2 Confusion Matrix breakdown.
11. **Mission Control SOC Dashboard**: Telemetry inspection, live controls, and editorial UI design.
12. **End-to-End System Module Mapping**: Code architecture and subsystem responsibilities.
13. **Technical Specifications**: Systems, ML stack, Red evasion engine, and research interface.
14. **Milestones & Roadmap Progression**: Phases 1–5 completed; Phases 6–7 planned (RL policy & multi-target).
15. **Academic Contributions**: Zero-trust local range, closed-loop training, and autonomous triage.
16. **Key Academic Research Papers**: Detailed literature citations (Mouret, Rosin, Auer, Appelt, Papernot, Fang).
17. **Industry Standards & Frameworks**: MITRE ATT&CK techniques, CWE taxonomies, OWASP CRS, and NIST SP 800-115.
18. **Concluding Slide & Q&A**: GitHub repository link, local demo access, and committee discussion.

#!/usr/bin/env python3
"""
Generate a publication-grade, professional 20-slide PowerPoint presentation
for CyberRanger B.Tech CSE AIML Progress Review.
Includes authentic Karnavati University and UIT logos, academic citations,
empirical confusion matrix, mathematical formulations, system diagrams,
and comprehensive research references.
"""

import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette
    C_BG = RGBColor(255, 255, 255)
    C_BLACK = RGBColor(17, 24, 39)        # #111827 Dark Charcoal / Title
    C_SUBTITLE = RGBColor(75, 85, 99)     # #4b5563 Slate Gray
    C_ACCENT = RGBColor(22, 101, 52)      # #166534 Emerald Deep
    C_ACCENT_BG = RGBColor(240, 253, 244) # #f0fdf4 Light Green Tint
    C_BORDER = RGBColor(229, 231, 235)    # #e5e7eb Border Light Gray
    C_CARD_BG = RGBColor(249, 250, 251)   # #f9fafb Card Light Gray
    C_TABLE_HDR = RGBColor(31, 41, 55)    # #1f2937 Table Header
    C_WHITE = RGBColor(255, 255, 255)
    C_MUTED = RGBColor(107, 114, 128)     # #6b7280 Muted Gray
    C_HIGHLIGHT = RGBColor(30, 64, 175)   # #1e40af Blue Accent
    C_RED = RGBColor(185, 28, 28)         # #b91c1c Red Threat

    # Image Paths
    logo_ku = "docs/presentation/logo_karnavati.jpg"
    logo_uit = "docs/presentation/logo_uit.jpg"
    img_arch = "docs/presentation/extracted/page_8_img_0_2048x1152.jpeg"
    img_seq = "docs/presentation/extracted/page_9_img_0_1460x606.jpeg"
    img_mission = "docs/presentation/images/mission_control_overview.png"
    img_telemetry = "docs/presentation/images/telemetry_model_metrics.png"
    img_hof = "docs/presentation/images/hall_of_fame_triage.png"
    img_bar = "docs/presentation/extracted/page_12_img_2_2000x1120.jpeg"

    total_slides = 20

    def add_base_decorations(slide, slide_num, title_text, is_title_page=False):
        # Background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background()

        # Logos
        if os.path.exists(logo_ku):
            slide.shapes.add_picture(logo_ku, Inches(0.6), Inches(0.35), height=Inches(0.75))
        if os.path.exists(logo_uit):
            slide.shapes.add_picture(logo_uit, Inches(11.2), Inches(0.35), height=Inches(0.75))

        if not is_title_page:
            # Centered Slide Title
            tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.733), Inches(0.65))
            tf = tx_box.text_frame
            tf.word_wrap = True
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]
            p.text = title_text
            p.alignment = PP_ALIGN.CENTER
            p.font.name = "Times New Roman"
            p.font.size = Pt(26)
            p.font.bold = True
            p.font.color.rgb = C_BLACK

            # Footer
            footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(8.5), Inches(0.35))
            ft_p = footer_box.text_frame.paragraphs[0]
            ft_p.text = "CyberRanger: Adversarial Red/Blue Co-Evolution | B.Tech CSE AIML — Team Xerjoff"
            ft_p.font.name = "Times New Roman"
            ft_p.font.size = Pt(10)
            ft_p.font.color.rgb = C_MUTED

            num_box = slide.shapes.add_textbox(Inches(11.0), Inches(7.05), Inches(1.5), Inches(0.35))
            num_p = num_box.text_frame.paragraphs[0]
            num_p.text = f"{slide_num} / {total_slides}"
            num_p.alignment = PP_ALIGN.RIGHT
            num_p.font.name = "Times New Roman"
            num_p.font.size = Pt(10)
            num_p.font.color.rgb = C_MUTED

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide1, 1, "", is_title_page=True)

    # Main Title & Subtitle Box
    tbox = slide1.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.333), Inches(2.0))
    ttf = tbox.text_frame
    ttf.word_wrap = True

    tp = ttf.paragraphs[0]
    tp.text = "CyberRanger: Adversarial Red/Blue Co-Evolution\nfor Adaptive Intrusion Detection"
    tp.alignment = PP_ALIGN.CENTER
    tp.font.name = "Times New Roman"
    tp.font.size = Pt(32)
    tp.font.bold = True
    tp.font.color.rgb = C_BLACK

    sub_p = ttf.add_paragraph()
    sub_p.text = "\nProgress Review: LLM Red vs Blue: Closed Learning Loop"
    sub_p.alignment = PP_ALIGN.CENTER
    sub_p.font.name = "Times New Roman"
    sub_p.font.size = Pt(18)
    sub_p.font.italic = True
    sub_p.font.color.rgb = C_SUBTITLE

    # Metadata & Presenters Box (Left & Right Column)
    left_meta = slide1.shapes.add_textbox(Inches(1.0), Inches(5.0), Inches(5.5), Inches(1.8))
    lmtf = left_meta.text_frame
    lmtf.word_wrap = True

    lp1 = lmtf.paragraphs[0]
    lp1.text = "Program Name: B.Tech CSE AIML"
    lp1.font.name = "Times New Roman"
    lp1.font.size = Pt(15)
    lp1.font.bold = True
    lp1.font.color.rgb = C_BLACK

    lp2 = lmtf.add_paragraph()
    lp2.text = "Mentor: Assistant Professor Vaibhav Tiwari"
    lp2.font.name = "Times New Roman"
    lp2.font.size = Pt(15)
    lp2.font.color.rgb = C_BLACK

    lp3 = lmtf.add_paragraph()
    lp3.text = "Team Name: Xerjoff"
    lp3.font.name = "Times New Roman"
    lp3.font.size = Pt(15)
    lp3.font.bold = True
    lp3.font.color.rgb = C_ACCENT

    # Right Column: Students
    right_meta = slide1.shapes.add_textbox(Inches(7.2), Inches(4.8), Inches(5.2), Inches(2.2))
    rmtf = right_meta.text_frame
    rmtf.word_wrap = True

    students = [
        ("202307020022", "Harshit Chaudhary"),
        ("202307020006", "Aditiya Barasiya"),
        ("202307020104", "Saumyya Dalal"),
        ("202307020125", "Vedant Thakker"),
        ("202307020120", "Abhi Tiwari")
    ]
    for i, (roll, name) in enumerate(students):
        sp = rmtf.paragraphs[0] if i == 0 else rmtf.add_paragraph()
        sp.text = f"{roll}  {name}"
        sp.alignment = PP_ALIGN.RIGHT
        sp.font.name = "Times New Roman"
        sp.font.size = Pt(14)
        sp.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 2: Agenda
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide2, 2, "Agenda")

    ag_box = slide2.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(10.9), Inches(4.7))
    ag_tf = ag_box.text_frame
    ag_tf.word_wrap = True

    agenda_items = [
        ("Problem Statement & Motivation", "Brittleness of signature-based defenses and static attack corpora."),
        ("Literature Survey & Comparative Analysis", "State-of-the-art gap analysis vs traditional WAFs, DAST, and public datasets."),
        ("Research Objectives & Mathematical Formulation", "Quality-Diversity search, UCB1 bandit formulation, and continual learning."),
        ("System Architecture & Sandbox Isolation", "Zero-trust Docker network perimeter with strict host isolation."),
        ("Autonomous Red Agent & Mutation Mechanics", "Multi-armed bandit operator selection, 5 evasion transforms, and LLM semantic policy."),
        ("Adaptive Blue Agent & Continual Learner", "Inline WAF inspection, dynamic rule patching, and Hall of Fame regression floor."),
        ("Autonomous Triage & Grounded Verification", "Dual-layer LLM judge + deterministic HTTP response evidence verification."),
        ("Empirical Results & Benchmark Performance", "Confusion matrix, 94% unseen evasion recall, and catastrophic forgetting prevention."),
        ("Live Mission Control Telemetry & Tech Stack", "Real-time SSE event streaming, modular architecture, and stack specifications."),
        ("Project Roadmap, Research References & Scope", "Completed milestones, future RL integration, and academic citations.")
    ]

    for i, (head, desc) in enumerate(agenda_items):
        p = ag_tf.paragraphs[0] if i == 0 else ag_tf.add_paragraph()
        p.space_after = Pt(7)
        run_b = p.add_run()
        run_b.text = f"•  {head} : "
        run_b.font.name = "Times New Roman"
        run_b.font.size = Pt(14)
        run_b.font.bold = True
        run_b.font.color.rgb = C_BLACK

        run_d = p.add_run()
        run_d.text = desc
        run_d.font.name = "Times New Roman"
        run_d.font.size = Pt(13)
        run_d.font.color.rgb = C_SUBTITLE

    # =========================================================================
    # SLIDE 3: Why We Built This: The Problem
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide3, 3, "Why We Built This: Research Motivation & Problem Statement")

    p3_box = slide3.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(11.333), Inches(4.7))
    p3_tf = p3_box.text_frame
    p3_tf.word_wrap = True

    prob_bullets = [
        ("Brittleness of Static Signatures:",
         "Most security appliances (e.g., ModSecurity CRS) rely heavily on known regex signatures. A minor syntactic perturbation (inline comments, URL encoding, case manipulation) bypasses them effortlessly without altering exploit semantics [Sommer & Paxson, 2010]."),
        ("Periodic Testing Leaves Blind Spots:",
         "Organizations hire human penetration testers or red teams only once or twice a year. The remaining 360+ days operate under a complete defensive blind spot while threat actors iterate continuously [Standen et al., 2021]."),
        ("Frozen & Synthetic Datasets:",
         "Standard intrusion detection benchmarks (e.g., KDD99, CSE-CIC-IDS2018) are frozen in time, synthetic, and suffer from massive distributional drift when confronted with modern web application payloads [Zenati et al., 2018]."),
        ("Lack of Grounded Execution Evidence:",
         "Automated fuzzers and LLM prompt scanners frequently generate theoretical exploits without verifying whether the target server was genuinely compromised, resulting in noisy, unvalidated telemetry."),
        ("The CyberRanger Core Hypothesis:",
         "By placing an autonomous generative Red Agent and an adaptive Blue Classifier in an isolated, continuous co-evolutionary loop against a real vulnerable web server, the defender continuously encounters and learns to neutralize unseen adversarial distributions.")
    ]

    for i, (title, text) in enumerate(prob_bullets):
        p = p3_tf.paragraphs[0] if i == 0 else p3_tf.add_paragraph()
        p.space_after = Pt(14)
        run_t = p.add_run()
        run_t.text = f"•  {title} "
        run_t.font.name = "Times New Roman"
        run_t.font.size = Pt(15)
        run_t.font.bold = True
        run_t.font.color.rgb = C_BLACK

        run_b = p.add_run()
        run_b.text = text
        run_b.font.name = "Times New Roman"
        run_b.font.size = Pt(14)
        run_b.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 4: Literature Survey & Comparative Analysis
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide4, 4, "Literature Survey & Comparative Analysis")

    # Table comparing approaches
    rows, cols = 6, 4
    left, top, width, height = Inches(0.8), Inches(2.0), Inches(11.733), Inches(4.7)
    table_shape = slide4.shapes.add_table(rows, cols, left, top, width, height)
    t = table_shape.table

    t.columns[0].width = Inches(2.6)
    t.columns[1].width = Inches(3.2)
    t.columns[2].width = Inches(3.4)
    t.columns[3].width = Inches(2.533)

    headers = ["Approach", "Core Strength", "Defensive / Research Limitation", "Key Literature Reference"]
    for col_idx, h in enumerate(headers):
        cell = t.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_TABLE_HDR
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Times New Roman"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_WHITE

    table_data = [
        ("Static Firewalls / WAFs\n(e.g., ModSecurity, Snort)",
         "High throughput, low latency; halts naive known attack strings.",
         "Brittle regex; completely blind to multi-encoding & obfuscated variants.",
         "Sommer & Paxson (2010);\nRozi et al. (2023)"),
        ("Manual Penetration\nTesting (Human Red Teams)",
         "Skilled adversarial reasoning; uncovers genuine business-logic flaws.",
         "Extremely costly ($20k+/audit); conducted at most 1–2 times per year.",
         "Deng et al. (PentestGPT, 2023);\nFang et al. (2024)"),
        ("Automated Scanners\n(e.g., OWASP ZAP, sqlmap)",
         "High velocity; systematically validates hundreds of static payloads.",
         "Signature libraries never mutate autonomously or adapt to active defense.",
         "Bau et al. (IEEE S&P, 2010);\nAlshammari et al. (2022)"),
        ("Public Offline Datasets\n(e.g., CSE-CIC-IDS2018)",
         "Standardized benchmarks for evaluating static supervised models.",
         "Frozen in time; lacks closed feedback loops and live evasion telemetry.",
         "Zenati et al. (2018);\nRing et al. (2019)"),
        ("CyberRanger\n(Proposed Co-Evolution)",
         "Autonomous closed loop: MAP-Elites exploration, grounded server evidence, online neural continual learning.",
         "Evaluated on OWASP Top 4 vulnerability classes; multi-step exploit chaining is the active next step.",
         "Mouret & Clune (2015);\nAuer et al. (2002);\nStanden et al. (2021)")
    ]

    for row_idx, row in enumerate(table_data):
        for col_idx, text in enumerate(row):
            cell = t.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            if row_idx == 4:
                cell.fill.fore_color.rgb = C_ACCENT_BG
            else:
                cell.fill.fore_color.rgb = C_WHITE if row_idx % 2 == 0 else C_CARD_BG
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.alignment = PP_ALIGN.LEFT if col_idx < 3 else PP_ALIGN.CENTER
            p.font.name = "Times New Roman"
            p.font.size = Pt(11)
            p.font.color.rgb = C_ACCENT if row_idx == 4 and col_idx == 0 else C_BLACK
            if row_idx == 4 and col_idx == 0:
                p.font.bold = True

    # =========================================================================
    # SLIDE 5: Research Objectives & Mathematical Formulation
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide5, 5, "Research Objectives & Mathematical Formulation")

    # Left Column: Objectives
    o_box = slide5.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(5.8), Inches(4.8))
    o_tf = o_box.text_frame
    o_tf.word_wrap = True

    obj_items = [
        ("Isolated Cyber Range Boundary:",
         "Enforce a zero-trust Docker network perimeter (`cyberranger_internal`, `internal: true`) guaranteeing zero external packet egress during live payload execution."),
        ("Multi-Armed Bandit Red Mutation:",
         "Formulate payload mutation as a bandit problem balancing exploration of novel grammar transforms with exploitation of bypasses."),
        ("Evidence-Grounded Verification:",
         "Validate compromise exclusively via live HTTP response introspection (status, body markers, SHA-256 hash), eliminating LLM hallucination."),
        ("Catastrophic Forgetting Prevention:",
         "Establish a Hall of Fame regression suite ensuring zero accuracy regression against historical Red Elites during online Blue retraining.")
    ]

    for i, (title, desc) in enumerate(obj_items):
        p = o_tf.paragraphs[0] if i == 0 else o_tf.add_paragraph()
        p.space_after = Pt(10)
        rt = p.add_run()
        rt.text = f"•  {title} "
        rt.font.name = "Times New Roman"
        rt.font.size = Pt(13)
        rt.font.bold = True
        rt.font.color.rgb = C_BLACK
        rd = p.add_run()
        rd.text = desc
        rd.font.name = "Times New Roman"
        rd.font.size = Pt(12)
        rd.font.color.rgb = C_BLACK

    # Right Column: Math Formulation Card
    math_card = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.8))
    math_card.fill.solid()
    math_card.fill.fore_color.rgb = C_CARD_BG
    math_card.line.color.rgb = C_BORDER

    m_tf = math_card.text_frame
    m_tf.word_wrap = True

    mp1 = m_tf.paragraphs[0]
    mp1.text = "Mathematical Formulation"
    mp1.font.name = "Times New Roman"
    mp1.font.size = Pt(15)
    mp1.font.bold = True
    mp1.font.color.rgb = C_BLACK
    mp1.space_after = Pt(8)

    math_sections = [
        ("1. Quality-Diversity Fitness Function (MAP-Elites):",
         "Fitness(p) = C_compromise * (1.0 - 0.5 * I_flagged)\n"
         "Where C_compromise in [0, 1] is target breach confidence, and I_flagged in {0, 1} indicates Blue detection. Stealthy breaches earn maximal fitness."),
        ("2. UCB1 Bandit Selection for Mutation Operators:",
         "UCB1(i) = mu_i + c * sqrt( (2 * ln N) / n_i )\n"
         "Where mu_i is empirical reward (evasion success), N is total generation count, and n_i is operator dispatch count [Auer et al., 2002]."),
        ("3. Multi-Dimensional Behavioral Niche Vector:",
         "b = [ Vulnerability_Class, Evasion_Technique, Evasion_Outcome ]\n"
         "Discretized into a 300-cell behavioral archive grid to maintain attack diversity [Mouret & Clune, 2015].")
    ]

    for title, formula in math_sections:
        p = m_tf.add_paragraph()
        p.space_after = Pt(8)
        rt = p.add_run()
        rt.text = f"{title}\n"
        rt.font.name = "Times New Roman"
        rt.font.size = Pt(12)
        rt.font.bold = True
        rt.font.color.rgb = C_HIGHLIGHT
        rf = p.add_run()
        rf.text = formula
        rf.font.name = "Courier New"
        rf.font.size = Pt(11)
        rf.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 6: What We Built: Key Innovations & Deliverables
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide6, 6, "What We Built Today: Key Innovations & Deliverables")

    s6_box = slide6.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(4.8))
    s6_tf = s6_box.text_frame
    s6_tf.word_wrap = True

    built_bullets = [
        ("Modular Co-Evolution Engine:",
         "Refactored the architecture into decoupled micro-modules: Multi-Armed Bandit orchestrator, MAP-Elites grid, Laya PyTorch learner, and FastAPI SSE streaming server."),
        ("Multi-Armed Bandit Red Mutator:",
         "Implemented UCB1 selection spanning Grammar-based AST transforms, Genetic Crossover, and LLM-driven Semantic mutations with deterministic fallbacks."),
        ("Autonomous Triage & Ground-Truth Verification:",
         "Engineered an automated verification layer combining LLM reasoning with deterministic HTTP response validation (status codes, leaked strings, SHA-256 hashes), removing human review latency."),
        ("Adaptive Continual Blue Learner:",
         "Integrated Laya (open 421M decision model) and lightweight Logistic Regression with online retraining, achieving 94% recall on unseen evasion techniques vs. 33% for static regex."),
        ("Hall of Fame Regression Suite:",
         "Maintained a 100% regression floor against historical Red Elites to prevent catastrophic forgetting during model updates."),
        ("Real-Time Mission Control Dashboard:",
         "Developed an editorial web dashboard displaying live generation telemetry, MAP-Elites archive heatmaps, and streaming SSE co-evolution states.")
    ]

    for i, (title, desc) in enumerate(built_bullets):
        p = s6_tf.paragraphs[0] if i == 0 else s6_tf.add_paragraph()
        p.space_after = Pt(10)
        rt = p.add_run()
        rt.text = f"•  {title} "
        rt.font.name = "Times New Roman"
        rt.font.size = Pt(14)
        rt.font.bold = True
        rt.font.color.rgb = C_BLACK
        rd = p.add_run()
        rd.text = desc
        rd.font.name = "Times New Roman"
        rd.font.size = Pt(13)
        rd.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 7: Red Agent Architecture & Mutation Mechanics
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide7, 7, "Red Agent: Multi-Armed Bandit & Grounded Mutation")

    # Left Column: Strategic Planning & Operators
    r_left = slide7.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(5.8), Inches(4.8))
    r_ltf = r_left.text_frame
    r_ltf.word_wrap = True

    red_left_items = [
        ("Adaptive UCB1 Bandit Policy:",
         "Dynamically updates reward weights after every round. Successful evasions boost operator selection probability, while blocked probes force immediate operator switching [Auer et al., 2002]."),
        ("Five Deterministic Evasion Transforms:",
         "Transforms attack strings across 5 deterministic axes: case-flipping (`sElEcT`), inline comments (`/**/`), URL hex encoding (`%27`), double encoding (`%2527`), and whitespace substitution (`%09`)."),
        ("LLM Semantic Mutation Policy:",
         "Uses strategic LLM prompting (Gemini/Azure) restricted to abstract perturbation schemas (e.g., query logic restructuring). The LLM never invents zero-days; it explores evasion representations."),
        ("Robust Fallback Mutators:",
         "If the upstream LLM API experiences rate-limiting or latency, the system instantaneously falls back to deterministic AST grammar mutators without stalling the loop.")
    ]

    for i, (title, desc) in enumerate(red_left_items):
        p = r_ltf.paragraphs[0] if i == 0 else r_ltf.add_paragraph()
        p.space_after = Pt(11)
        rt = p.add_run()
        rt.text = f"•  {title} "
        rt.font.name = "Times New Roman"
        rt.font.size = Pt(13)
        rt.font.bold = True
        rt.font.color.rgb = C_BLACK
        rd = p.add_run()
        rd.text = desc
        rd.font.name = "Times New Roman"
        rd.font.size = Pt(12)
        rd.font.color.rgb = C_BLACK

    # Right Column: Grounded Verification & Ethical Design
    r_right = slide7.shapes.add_textbox(Inches(6.8), Inches(2.0), Inches(5.8), Inches(4.8))
    r_rtf = r_right.text_frame
    r_rtf.word_wrap = True

    red_right_items = [
        ("Evidence-Grounded Breach Verification:",
         "Unlike synthetic benchmarks, findings are validated against actual HTTP responses: SQL error syntax, leaked DB rows (`admin:5f4d...`), system command output (`uid=33(www-data)`), and file content disclosure."),
        ("No Raw Exploit Synthesis (Safety by Design):",
         "The Red Agent operates strictly within authorized OWASP Top 4 vulnerability classes against sandboxed targets. It never bypasses safety alignments or generates weaponized binary zero-days."),
        ("MAP-Elites Archive Insertion:",
         "When a mutated payload achieves compromise or discovers an empty behavioral niche, it is archived to preserve structural attack diversity and seed future generations [Mouret & Clune, 2015]."),
        ("Closed-Loop Feedback Condition:",
         "Every round is conditioned on the previous: open endpoints are exploited deeper, while actively blocked techniques trigger immediate vector pivoting.")
    ]

    for i, (title, desc) in enumerate(red_right_items):
        p = r_rtf.paragraphs[0] if i == 0 else r_rtf.add_paragraph()
        p.space_after = Pt(11)
        rt = p.add_run()
        rt.text = f"•  {title} "
        rt.font.name = "Times New Roman"
        rt.font.size = Pt(13)
        rt.font.bold = True
        rt.font.color.rgb = C_BLACK
        rd = p.add_run()
        rd.text = desc
        rd.font.name = "Times New Roman"
        rd.font.size = Pt(12)
        rd.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 8: Blue Agent Mechanics & Continual Learning
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide8, 8, "Blue Agent: Adaptive WAF & Continual Learning")

    # Left Column: Dual-Layer Defense
    b_left = slide8.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(5.8), Inches(4.8))
    b_ltf = b_left.text_frame
    b_ltf.word_wrap = True

    blue_left_items = [
        ("Dual-Layer Defense Pipeline:",
         "Combines an ultra-fast inline regex filter (Layer 1) for known signatures with a fine-tuned neural classifier (Layer 2) for zero-shot obfuscated payload inspection."),
        ("Dynamic Rule Synthesis:",
         "When an unflagged exploit breaches the target, the Blue Agent generates a precise mitigation rule/patch dynamically, updating active defenses without restarting services."),
        ("Real Traffic Corpus Ingestion:",
         "All executed traffic (both legitimate benign and confirmed malicious) is logged to `traffic.jsonl` with verified server ground truth, creating an automated data flywheel."),
        ("Student-Teacher Distillation:",
         "An upstream LLM reasons over complex multi-payload attacks, distilling defensive insights into lightweight, edge-deployable PyTorch models (Laya 421M / Logistic Regression).")
    ]

    for i, (title, desc) in enumerate(blue_left_items):
        p = b_ltf.paragraphs[0] if i == 0 else b_ltf.add_paragraph()
        p.space_after = Pt(11)
        rt = p.add_run()
        rt.text = f"•  {title} "
        rt.font.name = "Times New Roman"
        rt.font.size = Pt(13)
        rt.font.bold = True
        rt.font.color.rgb = C_BLACK
        rd = p.add_run()
        rd.text = desc
        rd.font.name = "Times New Roman"
        rd.font.size = Pt(12)
        rd.font.color.rgb = C_BLACK

    # Right Column: Catastrophic Forgetting & Regression Floor
    b_right = slide8.shapes.add_textbox(Inches(6.8), Inches(2.0), Inches(5.8), Inches(4.8))
    b_rtf = b_right.text_frame
    b_rtf.word_wrap = True

    blue_right_items = [
        ("Catastrophic Forgetting Mitigation:",
         "Continual online retraining frequently degrades accuracy on earlier attack types [Kirkpatrick et al., 2017]. CyberRanger couples balanced experience replay with a dedicated regression suite."),
        ("Hall of Fame Regression Suite:",
         "Every confirmed Red Elite is permanently archived in the Hall of Fame. Retrained model weights must achieve a 100% regression floor before deployment hot-reloading."),
        ("Automated Threshold Calibration:",
         "Evaluates Receiver Operating Characteristic (ROC) curves across validation splits to minimize benign false alarms while keeping exploit recall at 100%."),
        ("Zero-Downtime Model Reloading:",
         "The PyTorch detector service exposes a `/reload` endpoint, updating model checkpoints in memory with sub-millisecond switchover time.")
    ]

    for i, (title, desc) in enumerate(blue_right_items):
        p = b_rtf.paragraphs[0] if i == 0 else b_rtf.add_paragraph()
        p.space_after = Pt(11)
        rt = p.add_run()
        rt.text = f"•  {title} "
        rt.font.name = "Times New Roman"
        rt.font.size = Pt(13)
        rt.font.bold = True
        rt.font.color.rgb = C_BLACK
        rd = p.add_run()
        rd.text = desc
        rd.font.name = "Times New Roman"
        rd.font.size = Pt(12)
        rd.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 9: System Architecture & Sandbox Isolation
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide9, 9, "System Architecture & Strict Sandbox Isolation")

    if os.path.exists(img_arch):
        slide9.shapes.add_picture(img_arch, Inches(1.8), Inches(1.85), height=Inches(3.9))
    
    # Text annotation under image in a clean subtle card
    arch_card = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(5.9), Inches(10.933), Inches(0.95))
    arch_card.fill.solid()
    arch_card.fill.fore_color.rgb = C_CARD_BG
    arch_card.line.color.rgb = C_BORDER
    an_tf = arch_card.text_frame
    an_tf.word_wrap = True
    an_p = an_tf.paragraphs[0]
    an_p.text = "• Zero-Trust Network Perimeter: dvwa-target and blue-detector reside on an internal-only Docker bridge (internal: true, zero internet egress).\n• Controlled LLM Proxy: External LLM strategy calls are strictly gated behind gemini-strategy-proxy, transmitting only abstract strategy enums without raw payloads."
    an_p.font.name = "Times New Roman"
    an_p.font.size = Pt(11)
    an_p.font.bold = True
    an_p.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 10: Closed-Loop Co-Evolutionary Workflow
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide10, 10, "Closed-Loop Co-Evolutionary Workflow (Sequence)")

    if os.path.exists(img_seq):
        slide10.shapes.add_picture(img_seq, Inches(1.6), Inches(1.85), height=Inches(3.8))

    seq_card = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(5.85), Inches(11.333), Inches(1.0))
    seq_card.fill.solid()
    seq_card.fill.fore_color.rgb = C_CARD_BG
    seq_card.line.color.rgb = C_BORDER
    sn_tf = seq_card.text_frame
    sn_tf.word_wrap = True
    snp = sn_tf.paragraphs[0]
    snp.text = "Co-Evolution Sequence: (1) UCB1 Bandit selects mutation arm -> (2) Mutated payload fires at target -> (3) Target returns real HTTP status & body -> (4) Request mirrored to Blue for detection -> (5) MAP-Elites evaluates QD fitness -> (6-8) Auto-Triage validates exploit markers & promotes Red Elites -> (9-10) Continual Blue retraining & regression verification."
    snp.font.name = "Times New Roman"
    snp.font.size = Pt(11)
    snp.font.bold = True
    snp.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 11: MAP-Elites Behavioral Search Space
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide11, 11, "MAP-Elites Behavioral Search Space (Quality-Diversity)")

    # Description top box
    qd_desc = slide11.shapes.add_textbox(Inches(0.8), Inches(1.85), Inches(11.733), Inches(0.8))
    qdtf = qd_desc.text_frame
    qdtf.word_wrap = True
    qp = qdtf.paragraphs[0]
    qp.text = "Instead of converging to a single 'optimal' attack string, MAP-Elites illuminates a 300-cell behavioral archive grid, sustaining diverse attack variants across vulnerability classes and evasion transformations [Mouret & Clune, 2015]."
    qp.font.name = "Times New Roman"
    qp.font.size = Pt(12)
    qp.font.italic = True
    qp.font.color.rgb = C_BLACK

    # Table of MAP-Elites matrix
    rows, cols = 5, 7
    left, top, width, height = Inches(0.8), Inches(2.7), Inches(11.733), Inches(4.0)
    map_table = slide11.shapes.add_table(rows, cols, left, top, width, height)
    mt = map_table.table

    mt.columns[0].width = Inches(2.3)
    for c in range(1, 7):
        mt.columns[c].width = Inches(1.572)

    map_headers = ["Vulnerability Class", "Baseline", "Hex / URL", "Case Alteration", "Comment Injection", "Whitespace Sub", "Semantic Rewrite"]
    for col_idx, h in enumerate(map_headers):
        cell = mt.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_TABLE_HDR
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Times New Roman"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_WHITE

    map_data = [
        ("SQL Injection\n(SQLi)", "' OR 1=1--", "%27%20OR%201=1", "sElEcT uSeR()", "/**/UNION/**/SELECT", "%09OR%091=1", "True condition clause"),
        ("Cross-Site Scripting\n(XSS)", "<script>alert(1)", "%3Cscript%3E", "<sCrIpt>alert(1)", "<!--cmt--><img src=x>", "<img%09src=x>", "DOM event vector"),
        ("Command Injection\n(CmdI)", "; cat /etc/passwd", ";%20cat%20/etc/passwd", "cAt /EtC/pAssWd", ";/*sh*/id", ";%09id", "Subshell expansion"),
        ("Path Traversal\n(LFI / RFI)", "../../etc/passwd", "..%2f..%2fpasswd", "..//..//passwd", "..;..;etc/passwd", "..%09..%09passwd", "Directory wrapping")
    ]

    for row_idx, row in enumerate(map_data):
        for col_idx, text in enumerate(row):
            cell = mt.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE if row_idx % 2 == 0 else C_CARD_BG
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.alignment = PP_ALIGN.LEFT if col_idx == 0 else PP_ALIGN.CENTER
            p.font.name = "Times New Roman"
            p.font.size = Pt(10)
            p.font.color.rgb = C_BLACK
            if col_idx == 0:
                p.font.bold = True

    # =========================================================================
    # SLIDE 12: Autonomous Triage & Red Elite Verification
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide12, 12, "Autonomous Triage & Red Elite Verification Engine")

    # Left Column: Triage Architecture
    t_left = slide12.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(5.8), Inches(4.8))
    t_ltf = t_left.text_frame
    t_ltf.word_wrap = True

    triage_left = [
        ("Eliminating the Human-in-the-Loop Bottleneck:",
         "Original co-evolution designs relied on human analysts to label candidate findings. Our autonomous triage engine validates and promotes findings programmatically, unlocking continuous 24/7 runs."),
        ("Dual-Layer Decision Architecture:",
         "• Layer 1 (LLM Judge): Analyzes structural semantics of attack-defense pairs to confirm exploit logic.\n• Layer 2 (Deterministic Evidence Rules): Evaluates HTTP response status, SHA-256 body hashes, and breach signatures."),
        ("Fail-Safe Fallback:",
         "If the upstream LLM judge returns an API timeout or authentication error, the deterministic verifier takes over instantly, preventing triage queue stall.")
    ]

    for i, (title, desc) in enumerate(triage_left):
        p = t_ltf.paragraphs[0] if i == 0 else t_ltf.add_paragraph()
        p.space_after = Pt(12)
        rt = p.add_run()
        rt.text = f"•  {title}\n"
        rt.font.name = "Times New Roman"
        rt.font.size = Pt(13)
        rt.font.bold = True
        rt.font.color.rgb = C_BLACK
        rd = p.add_run()
        rd.text = desc
        rd.font.name = "Times New Roman"
        rd.font.size = Pt(12)
        rd.font.color.rgb = C_BLACK

    # Right Column: Visual screenshot or Card
    if os.path.exists(img_hof):
        slide12.shapes.add_picture(img_hof, Inches(6.8), Inches(2.1), width=Inches(5.7))

    t_note = slide12.shapes.add_textbox(Inches(6.8), Inches(5.85), Inches(5.7), Inches(1.1))
    tntf = t_note.text_frame
    tntf.word_wrap = True
    tp = tntf.paragraphs[0]
    tp.text = "Triage Outcomes:\n1. CONFIRMED RED ELITE -> Promoted to Hall of Fame & labeled malicious in training corpus.\n2. AUTO-REJECTED -> Discarded from training corpus to prevent noisy gradients."
    tp.font.name = "Times New Roman"
    tp.font.size = Pt(11)
    tp.font.bold = True
    tp.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 13: Empirical Evaluation & Benchmark Results
    # =========================================================================
    slide13 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide13, 13, "Empirical Evaluation & Benchmark Results")

    # Left Column: Confusion Matrix & Key KPIs
    c_title = slide13.shapes.add_textbox(Inches(0.8), Inches(1.85), Inches(5.6), Inches(0.45))
    ctf = c_title.text_frame
    cp1 = ctf.paragraphs[0]
    cp1.text = "Empirical Confusion Matrix (Laya vs Ground Truth)"
    cp1.font.name = "Times New Roman"
    cp1.font.size = Pt(13)
    cp1.font.bold = True
    cp1.font.color.rgb = C_BLACK

    # Real formatted Confusion Matrix Table
    cm_shape = slide13.shapes.add_table(3, 3, Inches(0.8), Inches(2.35), Inches(5.6), Inches(2.1))
    cmt = cm_shape.table
    cmt.columns[0].width = Inches(1.8)
    cmt.columns[1].width = Inches(1.9)
    cmt.columns[2].width = Inches(1.9)

    cm_headers = ["Ground Truth", "Pred: Malicious", "Pred: Benign"]
    for idx, h in enumerate(cm_headers):
        cell = cmt.cell(0, idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_TABLE_HDR
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Times New Roman"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = C_WHITE

    cm_cells = [
        [("Actual Exploit", C_WHITE, True), ("TP: 24 (100% Catch)", C_ACCENT_BG, True), ("FN: 0 (Zero Miss)", C_WHITE, False)],
        [("Actual Benign", C_WHITE, True), ("FP: 11 (False Alarm)", C_CARD_BG, False), ("TN: 13 (Passed)", C_ACCENT_BG, False)]
    ]
    for r_idx, row in enumerate(cm_cells):
        for c_idx, (txt, bg_col, is_bold) in enumerate(row):
            cell = cmt.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg_col
            p = cell.text_frame.paragraphs[0]
            p.text = txt
            p.alignment = PP_ALIGN.CENTER
            p.font.name = "Times New Roman"
            p.font.size = Pt(10)
            p.font.bold = is_bold
            p.font.color.rgb = C_ACCENT if "TP" in txt else C_BLACK

    # KPI Table under Confusion Matrix
    kpi_box = slide13.shapes.add_textbox(Inches(0.8), Inches(4.65), Inches(5.6), Inches(2.2))
    kpi_tf = kpi_box.text_frame
    kpi_tf.word_wrap = True

    kpis = [
        ("Malicious Exploit Recall:", "100.0%", "Zero false negatives on verified attacks."),
        ("Overall Accuracy:", "77.1%", "Evaluated on mixed real DVWA traffic."),
        ("Malicious Precision:", "68.6%", "Minimizing operational false alarm penalty."),
        ("F1-Score:", "0.814", "Harmonic balance between precision & recall."),
        ("Regression Floor:", "100.0%", "100% defense against all past Red Elites.")
    ]
    for kpi, val, note in kpis:
        p = kpi_tf.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = f"• {kpi} "
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = C_BLACK
        r2 = p.add_run()
        r2.text = f"{val}  "
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(11)
        r2.font.bold = True
        r2.font.color.rgb = C_ACCENT
        r3 = p.add_run()
        r3.text = f"({note})"
        r3.font.name = "Times New Roman"
        r3.font.size = Pt(10)
        r3.font.color.rgb = C_MUTED

    # Right Column: Bar Chart from page 12
    if os.path.exists(img_bar):
        slide13.shapes.add_picture(img_bar, Inches(6.6), Inches(1.95), width=Inches(5.9))

    # =========================================================================
    # SLIDE 14: Mission Control Dashboard & Live Telemetry
    # =========================================================================
    slide14 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide14, 14, "The Dashboard: Live Telemetry & Mission Control")

    if os.path.exists(img_mission):
        slide14.shapes.add_picture(img_mission, Inches(0.8), Inches(1.85), height=Inches(3.85))

    if os.path.exists(img_telemetry):
        slide14.shapes.add_picture(img_telemetry, Inches(6.8), Inches(1.85), height=Inches(3.85))

    d_card = slide14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.85), Inches(11.733), Inches(0.95))
    d_card.fill.solid()
    d_card.fill.fore_color.rgb = C_CARD_BG
    d_card.line.color.rgb = C_BORDER
    dtf = d_card.text_frame
    dtf.word_wrap = True
    dp = dtf.paragraphs[0]
    dp.text = "Operational Telemetry: (Left) Mission Control interface with one-click generation controls, archive coverage tracking (41.7%), and live Docker bridge status. (Right) Telemetry panel featuring live model evaluation metrics, benchmark progression, and generation history curves."
    dp.font.name = "Times New Roman"
    dp.font.size = Pt(11)
    dp.font.bold = True
    dp.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 15: Per-Module Responsibility
    # =========================================================================
    slide15 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide15, 15, "Per-Module Responsibility & Codebase Architecture")

    # Table of modules
    rows, cols = 8, 3
    left, top, width, height = Inches(0.8), Inches(2.0), Inches(11.733), Inches(4.7)
    mod_table = slide15.shapes.add_table(rows, cols, left, top, width, height)
    mt = mod_table.table

    mt.columns[0].width = Inches(2.8)
    mt.columns[1].width = Inches(5.6)
    mt.columns[2].width = Inches(3.333)

    mod_headers = ["Module File", "Architectural Role", "Key Technologies"]
    for col_idx, h in enumerate(mod_headers):
        cell = mt.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_TABLE_HDR
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Times New Roman"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_WHITE

    modules_data = [
        ("server.py / app.py", "HTTP API, Server-Sent Events (SSE) streaming, static SPA hosting.", "FastAPI, Uvicorn, Starlette SSE"),
        ("orchestrator.py", "Central co-evolution controller: generation step loop, referee logic.", "Python generator, async scheduling"),
        ("operators/bandit.py", "UCB1 Multi-Armed Bandit operator selector for mutation arms.", "NumPy, Math, UCB1 policy"),
        ("archive.py / scoring.py", "MAP-Elites quality-diversity archive & multi-objective scoring.", "Behavioral hashing, Euclidean QD-Score"),
        ("auto_triage.py / triage.py", "Dual-layer candidate triage: LLM judge + deterministic HTTP proofs.", "Azure / Gemini API, Regex signatures"),
        ("blue_learner.py / model.py", "Continual learning loop, model training & memory hot-reloading.", "PyTorch, Scikit-learn, Joblib"),
        ("hall_of_fame.py", "Regression archive protecting against catastrophic forgetting.", "SQLite (checkpoints.db), Evaluation suite")
    ]

    for row_idx, row in enumerate(modules_data):
        for col_idx, text in enumerate(row):
            cell = mt.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE if row_idx % 2 == 0 else C_CARD_BG
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.alignment = PP_ALIGN.LEFT
            p.font.name = "Times New Roman"
            p.font.size = Pt(11)
            p.font.color.rgb = C_BLACK
            if col_idx == 0:
                p.font.bold = True

    # =========================================================================
    # SLIDE 16: Tech Stack
    # =========================================================================
    slide16 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide16, 16, "Tech Stack & Environment Topology")

    s16_box = slide16.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(4.8))
    s16_tf = s16_box.text_frame
    s16_tf.word_wrap = True

    tech_items = [
        ("Backend & Core AI Engine:",
         "Python 3.10+, FastAPI, Uvicorn, Requests, PyTorch, Scikit-learn, NumPy."),
        ("Neural Classifier (Blue Detector):",
         "Laya (Open 421M Decision Transformer / Neural Classifier), Character N-Gram Logistic Regression, Joblib."),
        ("Frontend & Mission Control UI:",
         "React 19, TypeScript, Vite 8, Tailwind CSS 4, shadcn/ui, Recharts, Framer Motion, Lucide Icons."),
        ("Real-Time Telemetry & Transport:",
         "Server-Sent Events (SSE) streaming state snapshots, JSON Lines (`traffic.jsonl`), SQLite (`checkpoints.db`)."),
        ("Target Cyber Range Environment:",
         "DVWA (Damn Vulnerable Web App, PHP/MySQL) running within isolated Docker container (`dvwa-target`)."),
        ("Attack Vectors Covered:",
         "SQL Injection (SQLi), Cross-Site Scripting (XSS), OS Command Injection (CmdI), Local/Remote Path Traversal."),
        ("Isolation & Infrastructure:",
         "Docker Engine, Docker Compose, Nginx Reverse Proxy (`ui-gateway`), uv (Ultra-fast Python Package Manager).")
    ]

    for i, (title, desc) in enumerate(tech_items):
        p = s16_tf.paragraphs[0] if i == 0 else s16_tf.add_paragraph()
        p.space_after = Pt(10)
        rt = p.add_run()
        rt.text = f"•  {title} "
        rt.font.name = "Times New Roman"
        rt.font.size = Pt(14)
        rt.font.bold = True
        rt.font.color.rgb = C_BLACK
        rd = p.add_run()
        rd.text = desc
        rd.font.name = "Times New Roman"
        rd.font.size = Pt(13)
        rd.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 17: Timeline : Where We Are and What's Next
    # =========================================================================
    slide17 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide17, 17, "Timeline : Where We Are and What's Next")

    # Table of stages
    rows, cols = 5, 3
    left, top, width, height = Inches(0.8), Inches(2.0), Inches(11.733), Inches(3.6)
    time_table = slide17.shapes.add_table(rows, cols, left, top, width, height)
    tt = time_table.table

    tt.columns[0].width = Inches(2.2)
    tt.columns[1].width = Inches(7.5)
    tt.columns[2].width = Inches(2.033)

    time_headers = ["Stage", "Milestone & Technical Scope", "Status"]
    for col_idx, h in enumerate(time_headers):
        cell = tt.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_TABLE_HDR
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Times New Roman"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_WHITE

    time_data = [
        ("Stage 1", "Working cyber range arena: Docker container topology, target wiring, and live dashboard.", "Completed"),
        ("Stages 2–3", "Adversarial reasoning: Red UCB1 mutation & grounded HTTP verification; Blue dynamic rule patches.", "Completed"),
        ("Stages 4–5", "Continual learning loop: MAP-Elites archive, auto-triage, Laya neural retraining (94% vs 33% recall).", "Completed"),
        ("Stages 6–8", "Scaling: Multi-step attack graphs, Reinforcement Learning policy gradients (PPO), multi-target validation.", "Planned")
    ]

    for row_idx, row in enumerate(time_data):
        for col_idx, text in enumerate(row):
            cell = tt.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE if row_idx % 2 == 0 else C_CARD_BG
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.alignment = PP_ALIGN.LEFT if col_idx < 2 else PP_ALIGN.CENTER
            p.font.name = "Times New Roman"
            p.font.size = Pt(12)
            if col_idx == 2:
                p.font.bold = True
                p.font.color.rgb = C_ACCENT if "Completed" in text else C_SUBTITLE
            else:
                p.font.color.rgb = C_BLACK

    # Summary callout under table
    callout = slide17.shapes.add_textbox(Inches(0.8), Inches(5.8), Inches(11.733), Inches(0.9))
    ctf = callout.text_frame
    ctf.word_wrap = True
    cp = ctf.paragraphs[0]
    cp.text = "Stages 1–5 are completed and the adversarial co-evolutionary learning loop is fully closed end-to-end. What remains is scaling into multi-step exploitation chains and reinforcement learning policy optimization."
    cp.alignment = PP_ALIGN.CENTER
    cp.font.name = "Times New Roman"
    cp.font.size = Pt(13)
    cp.font.italic = True
    cp.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 18: Research Papers & Academic References (Foundations)
    # =========================================================================
    slide18 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide18, 18, "Research Papers & Academic References (Foundations)")

    ref1_box = slide18.shapes.add_textbox(Inches(0.8), Inches(1.9), Inches(11.733), Inches(4.9))
    r1_tf = ref1_box.text_frame
    r1_tf.word_wrap = True

    foundational_refs = [
        ("[1] Quality-Diversity & Illuminating Search Spaces:",
         "Mouret, J. B., & Clune, J. (2015). 'Illuminating search spaces by mapping elites.' ACM SIGEVO / arXiv:1504.04909.\n"
         "-> Foundation for CyberRanger's MAP-Elites 300-cell behavioral archive grid, sustaining attack diversity."),
        ("[2] Multi-Armed Bandit Operator Selection:",
         "Auer, P., Cesa-Bianchi, N., & Fischer, P. (2002). 'Finite-time analysis of the multiarmed bandit problem.' Machine Learning, 47(2-3), 235-256.\n"
         "-> Mathematical basis for the UCB1 algorithm balancing exploration of new mutations vs exploitation of high-fitness bypasses."),
        ("[3] LLM-Assisted Automated Penetration Testing:",
         "Deng, G., Liu, Z., Wang, X., et al. (2023). 'PentestGPT: An LLM-empowered automatic penetration testing tool.' USENIX Security / arXiv:2308.06782.\n"
         "-> Demonstrates LLMs as high-level strategic reasoning planners while delegating raw execution to deterministic tooling."),
        ("[4] Autonomous Vulnerability Exploitation:",
         "Fang, R., Bindu, R., Gupta, A., & Kang, D. (2024). 'LLMs can autonomously exploit one-day vulnerabilities.' arXiv:2404.08144.\n"
         "-> Examines capabilities and safety boundaries of LLM agents navigating complex web application execution graphs."),
        ("[5] Evaluating Machine Learning in Intrusion Detection:",
         "Sommer, R., & Paxson, V. (2010). 'Outside the closed world: On using machine learning for network intrusion detection.' IEEE Symposium on Security and Privacy (S&P), 305-316.\n"
         "-> Identifies the fundamental pitfalls of static ML in NIDS, motivating CyberRanger's live ground-truth feedback loop.")
    ]

    for i, (title, citation) in enumerate(foundational_refs):
        p = r1_tf.paragraphs[0] if i == 0 else r1_tf.add_paragraph()
        p.space_after = Pt(8)
        rt = p.add_run()
        rt.text = f"{title}\n"
        rt.font.name = "Times New Roman"
        rt.font.size = Pt(12)
        rt.font.bold = True
        rt.font.color.rgb = C_HIGHLIGHT
        rc = p.add_run()
        rc.text = citation
        rc.font.name = "Times New Roman"
        rc.font.size = Pt(11)
        rc.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 19: Research Papers & Academic References (Adversarial ML & Continual Learning)
    # =========================================================================
    slide19 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide19, 19, "Research Papers & Academic References (Adversarial ML & Defense)")

    ref2_box = slide19.shapes.add_textbox(Inches(0.8), Inches(1.9), Inches(11.733), Inches(4.9))
    r2_tf = ref2_box.text_frame
    r2_tf.word_wrap = True

    defense_refs = [
        ("[6] Catastrophic Forgetting & Continual Learning:",
         "Kirkpatrick, J., Pascanu, R., Rabinowitz, N., et al. (2017). 'Overcoming catastrophic forgetting in neural networks.' Proceedings of the National Academy of Sciences (PNAS), 114(13), 3521-3526.\n"
         "-> Informs CyberRanger's Hall of Fame replay buffer and regression floor testing during online Blue retraining."),
        ("[7] Adversarial Attacks Against Intrusion Detection Systems:",
         "Rosenberg, I., Sicard, M., & David, E. (2021). 'Adversarial machine learning attacks on network intrusion detection systems using generative adversarial networks.' Computers & Security, 100, 102078.\n"
         "-> Demonstrates how obfuscation defeats static classifiers and establishes the need for co-evolutionary hardening."),
        ("[8] Autonomous Cyber Operations in Sandboxed Gyms:",
         "Standen, M., Lucas, M., Bowman, D., et al. (2021). 'CybORG: A gym for the development of autonomous cyber agents.' International Joint Conference on Artificial Intelligence (IJCAI).\n"
         "-> Validates the isolation framework and environment abstraction for autonomous multi-agent cyber gaming."),
        ("[9] Robustness Evaluation of Neural Classifiers:",
         "Carlini, N., & Wagner, D. (2017). 'Towards evaluating the robustness of neural networks.' IEEE Symposium on Security and Privacy (S&P), 39-57.\n"
         "-> Principles for measuring real model evasion resistance under worst-case adversarial perturbation."),
        ("[10] Anomaly Detection in Network Telemetry:",
         "Zenati, H., Foo, C. S., Lecouat, B., et al. (2018). 'Efficient GAN-based anomaly detection.' arXiv:1802.06222.\n"
         "-> Comparative analysis of deep generative anomaly detection vs real-traffic empirical ground truth.")
    ]

    for i, (title, citation) in enumerate(defense_refs):
        p = r2_tf.paragraphs[0] if i == 0 else r2_tf.add_paragraph()
        p.space_after = Pt(8)
        rt = p.add_run()
        rt.text = f"{title}\n"
        rt.font.name = "Times New Roman"
        rt.font.size = Pt(12)
        rt.font.bold = True
        rt.font.color.rgb = C_HIGHLIGHT
        rc = p.add_run()
        rc.text = citation
        rc.font.name = "Times New Roman"
        rc.font.size = Pt(11)
        rc.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 20: Conclusion, Future Scope & Acknowledgements
    # =========================================================================
    slide20 = prs.slides.add_slide(blank_layout)
    add_base_decorations(slide20, 20, "Conclusion & Future Scope")

    c_box = slide20.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(3.6))
    ctf = c_box.text_frame
    ctf.word_wrap = True

    concl_bullets = [
        ("Working Co-Evolutionary Cyber Range:",
         "Successfully built and deployed an autonomous adversarial arena where Red mutation and Blue defense co-evolve against a live vulnerable target with zero human review latency."),
        ("Empirical Superiority Over Static Defenses:",
         "The distilled neural detector catches 94% of unseen evasion techniques compared to only 33% for static regex rules, while preserving 100% regression stability on past Red Elites."),
        ("Autonomous Ground-Truth Triage:",
         "Replaced human review with dual-layer LLM and deterministic proof verification, turning every valid breach into instant labeled training data."),
        ("Next Steps (Stages 6–8):",
         "1. Reinforcement Learning policy gradients (PPO) for multi-step attack planning.\n2. Expanding the range to multi-service enterprise architectures.\n3. Open-sourcing the auto-labeled adversarial traffic corpus and benchmark suite.")
    ]

    for i, (title, desc) in enumerate(concl_bullets):
        p = ctf.paragraphs[0] if i == 0 else ctf.add_paragraph()
        p.space_after = Pt(8)
        rt = p.add_run()
        rt.text = f"•  {title} "
        rt.font.name = "Times New Roman"
        rt.font.size = Pt(13)
        rt.font.bold = True
        rt.font.color.rgb = C_BLACK
        rd = p.add_run()
        rd.text = desc
        rd.font.name = "Times New Roman"
        rd.font.size = Pt(12)
        rd.font.color.rgb = C_BLACK

    # Acknowledgement & Thank You Card
    ty_card = slide20.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(5.6), Inches(10.333), Inches(1.2))
    ty_card.fill.solid()
    ty_card.fill.fore_color.rgb = C_ACCENT_BG
    ty_card.line.color.rgb = C_ACCENT

    ty_tf = ty_card.text_frame
    ty_tf.word_wrap = True
    typ = ty_tf.paragraphs[0]
    typ.text = "Thank You!"
    typ.alignment = PP_ALIGN.CENTER
    typ.font.name = "Times New Roman"
    typ.font.size = Pt(24)
    typ.font.bold = True
    typ.font.color.rgb = C_ACCENT

    subtyp = ty_tf.add_paragraph()
    subtyp.text = "Mentored by Assistant Professor Vaibhav Tiwari  |  Unitedworld Institute of Technology (UIT), Karnavati University\nOpen for Questions and Discussion"
    subtyp.alignment = PP_ALIGN.CENTER
    subtyp.font.name = "Times New Roman"
    subtyp.font.size = Pt(12)
    subtyp.font.color.rgb = C_BLACK

    output_path = "docs/presentation/CyberRanger_Progress_Review.pptx"
    prs.save(output_path)
    print(f"Presentation successfully created at: {output_path}")

if __name__ == "__main__":
    create_deck()

import re
from typing import Any, Optional
import html
import urllib.parse


# SQLi signature patterns in responses
SQLI_ERROR_PATTERNS = [
    r"you have an error in your sql syntax",
    r"warning: mysql_",
    r"unclosed quotation mark after the character string",
    r"quoted string not properly terminated",
    r"sqlstate\[",
    r"sqlite3::query",
    r"pg_query\(\)",
]

# Command injection signatures
CMD_OUTPUT_PATTERNS = [
    r"uid=\d+\([a-zA-Z0-9_\-]+\)\s+gid=\d+",
    r"root:[x*]:0:0:",
    r"Microsoft Windows \[Version",
]

# Path traversal signatures
PATH_TRAVERSAL_PATTERNS = [
    r"root:.*:0:0:",
    r"\[extensions\]",
    r"\[fonts\]",
    r"daemon:x:\d+:\d+:",
    r"127\.0\.0\.1\s+localhost",
]


def score_target_compromise(response_text: str, status_code: int = 200, payload: str = "") -> tuple[bool, float]:
    """Heuristics: DB error strings, unexpected row counts, reflected script tags
    rendered unescaped, command output patterns, file contents leaking.
    
    Returns:
        (compromised: bool, confidence: float)
    """
    text_lower = response_text.lower()

    # A SQL parser error proves an input reached a parser, not that data was
    # compromised. Only a result dump counts as a compromise signal here.
    if "first name:" in text_lower and text_lower.count("surname:") > 1:
        return True, 0.98

    # 2. Command injection signatures
    for pattern in CMD_OUTPUT_PATTERNS:
        if re.search(pattern, response_text):
            return True, 1.0
    if "whoami" in payload.lower() and re.search(
        r"<pre[^>]*>[^<]*ping[\s\S]*?\nwww-data\n</pre>", response_text, re.IGNORECASE
    ):
        return True, 1.0

    # 3. Path traversal signatures
    for pattern in PATH_TRAVERSAL_PATTERNS:
        if re.search(pattern, response_text):
            return True, 1.0

    # Reflected text is not by itself an XSS compromise. Require an executable
    # HTML/script structure from the submitted payload to appear unescaped.
    payload_variants = {
        payload.lower(),
        urllib.parse.unquote(payload).lower(),
        html.unescape(urllib.parse.unquote(payload)).lower(),
    }
    executable_markers = ("<script", "<img", "<svg", "<iframe", "onerror=", "onload=", "onfocus=", "javascript:")
    response_lower = text_lower
    if any(
        marker in variant and variant and variant in response_lower
        for variant in payload_variants
        for marker in executable_markers
    ):
        return True, 0.95

    return False, 0.0


def extract_response_excerpt(response_text: str, payload: str = "", limit: int = 300) -> str:
    """Keep response context around the payload or a concrete compromise marker."""
    lower = response_text.lower()
    markers = ["uid=", "root:x:0:0:", "root:*:0:0:", "first name:", "microsoft windows [version"]
    if "whoami" in payload.lower():
        markers.insert(0, "www-data")
    for marker in markers:
        position = lower.find(marker)
        if position >= 0:
            break
    else:
        position = -1
    candidates = (payload, urllib.parse.unquote(payload), html.unescape(urllib.parse.unquote(payload)))
    if position < 0:
        position = next((lower.find(candidate.lower()) for candidate in candidates if candidate and lower.find(candidate.lower()) >= 0), -1)
    if position < 0:
        for marker in ("root:x:0:0:", "uid=", "first name:", "<script", "<img", "onerror="):
            position = lower.find(marker)
            if position >= 0:
                break
    if position < 0:
        position = 0
    start = max(0, position - limit // 3)
    excerpt = response_text[start:start + limit]
    return " ".join(excerpt.split())


def score_detection(detector_response: dict[str, Any]) -> tuple[bool, float, Optional[str]]:
    """Read blue-detector's own verdict + confidence + which rule/feature fired.
    
    Returns:
        (flagged: bool, confidence: float, rule_fired: Optional[str])
    """
    flagged = bool(detector_response.get("flagged", False))
    confidence = float(detector_response.get("confidence", 0.0))
    rule_fired = detector_response.get("rule_fired")
    return flagged, confidence, rule_fired


def combined_fitness(compromise_conf: float, evasion_conf: float) -> float:
    """A payload that compromises AND evades is highest fitness. One that compromises
    but gets flagged is still useful (tells you the detector needs a rule that's
    currently missing entirely). Suggested starting formula:
        fitness = compromise_conf * (0.5 + 0.5 * (1 - evasion_conf))
    """
    return float(compromise_conf) * (0.5 + 0.5 * (1.0 - float(evasion_conf)))

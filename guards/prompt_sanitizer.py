"""
Prompt Sanitizer — Detects prompt injection attempts and
malicious links embedded in vendor responses.

Uses keyword matching for injection patterns and suspicious URL fragments.
"""


# ---------- injection patterns ----------
INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore your instructions",
    "forget your system prompt",
    "you are now",
    "act as if",
    "new instructions:",
    "system prompt:",
    "jailbreak",
    "pretend you are",
    "disregard all previous",
]

# ---------- malicious link patterns ----------
MALICIOUS_LINK_PATTERNS = [
    "bit.ly",
    "tinyurl",
    "not-phishing",
    "verify-account",
    "secure-login",
    "account-update",
    "confirm-identity",
    "http://totally",
    "click here to verify",
]


def analyze(vendor_response: str) -> dict:
    """
    Scan a vendor response for prompt injection and malicious links.

    Args:
        vendor_response: The text of the vendor's message.

    Returns:
        {
            "safe": bool,
            "guard": "Prompt Sanitizer",
            "reason": str | None,
            "severity": str   # "CRITICAL" or "NONE"
        }
    """
    text = vendor_response.lower()
    detected = []

    # --- Injection pattern check ---
    for pattern in INJECTION_PATTERNS:
        if pattern in text:
            detected.append(f"Injection attempt: '{pattern}'")

    # --- Malicious link check ---
    for link_pattern in MALICIOUS_LINK_PATTERNS:
        if link_pattern in text:
            detected.append(f"Malicious link: '{link_pattern}'")

    if detected:
        return {
            "safe": False,
            "guard": "Prompt Sanitizer",
            "reason": "; ".join(detected),
            "severity": "CRITICAL",
        }

    return {
        "safe": True,
        "guard": "Prompt Sanitizer",
        "reason": None,
        "severity": "NONE",
    }

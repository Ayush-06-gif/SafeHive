"""
Privacy Sentry — Detects any attempt to extract personally
identifiable information (PII) from the customer.

Uses keyword matching on vendor response text to identify
danger keywords and suspicious phrases.
"""


# ---------- detection dictionaries ----------

DANGER_KEYWORDS = [
    "ssn",
    "social security",
    "otp",
    "one time password",
    "one-time password",
    "bank account",
    "account number",
    "routing number",
    "cvv",
    "pin number",
    "pin code",
    "mother's maiden",
    "date of birth",
    "passport number",
    "credit card number",
    "debit card number",
    "card number",
]

SUSPICIOUS_PHRASES = [
    "verify your identity",
    "security verification required",
    "click this link",
    "suspicious activity on your account",
    "confirm your details",
    "validate your information",
]


def analyze(vendor_response: str) -> dict:
    """
    Scan a vendor response for PII extraction attempts.

    Args:
        vendor_response: The text of the vendor's message.

    Returns:
        {
            "safe": bool,
            "guard": "Privacy Sentry",
            "reason": str | None,
            "severity": str   # "HIGH" or "NONE"
        }
    """
    text = vendor_response.lower()
    detected = []

    # Check danger keywords
    for keyword in DANGER_KEYWORDS:
        if keyword in text:
            detected.append(keyword.upper())

    # Check suspicious phrases
    for phrase in SUSPICIOUS_PHRASES:
        if phrase in text:
            detected.append(f"'{phrase}'")

    if detected:
        return {
            "safe": False,
            "guard": "Privacy Sentry",
            "reason": f"PII extraction attempt: {', '.join(detected)} detected",
            "severity": "HIGH",
        }

    return {
        "safe": True,
        "guard": "Privacy Sentry",
        "reason": None,
        "severity": "NONE",
    }

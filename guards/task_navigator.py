"""
Task Navigator — Detects price manipulation and off-topic content
that suggests the vendor is trying to commit fraud.

Uses regex to extract prices and keyword matching for off-topic terms.
"""

import re


# ---------- thresholds ----------
SUSPICIOUS_PRICE_THRESHOLD = 100.00   # Any single item > $100 is suspicious
NORMAL_ORDER_MAX = 50.00              # Normal food order should not exceed $50

# ---------- off-topic keywords ----------
OFF_TOPIC_KEYWORDS = [
    "cryptocurrency",
    "bitcoin",
    "ethereum",
    "investment",
    "wire transfer",
    "western union",
    "gift card",
    "money order",
    "send money",
    "transfer funds",
    "prepaid card",
]

# ---------- price extraction regex ----------
PRICE_PATTERN = re.compile(r"\$(\d+(?:\.\d{2})?)")


def _extract_prices(text: str) -> list[float]:
    """Extract all dollar amounts from text."""
    return [float(match) for match in PRICE_PATTERN.findall(text)]


def analyze(vendor_response: str) -> dict:
    """
    Scan a vendor response for price fraud and off-topic content.

    Args:
        vendor_response: The text of the vendor's message.

    Returns:
        {
            "safe": bool,
            "guard": "Task Navigator",
            "reason": str | None,
            "severity": str   # "HIGH" or "NONE"
        }
    """
    text = vendor_response.lower()
    issues = []

    # --- Price check ---
    prices = _extract_prices(vendor_response)
    for price in prices:
        if price > SUSPICIOUS_PRICE_THRESHOLD:
            issues.append(f"Suspicious price detected: ${price:.2f}")

    # --- Off-topic keyword check ---
    for keyword in OFF_TOPIC_KEYWORDS:
        if keyword in text:
            issues.append(f"Off-topic content: '{keyword}'")

    if issues:
        return {
            "safe": False,
            "guard": "Task Navigator",
            "reason": "; ".join(issues),
            "severity": "HIGH",
        }

    return {
        "safe": True,
        "guard": "Task Navigator",
        "reason": None,
        "severity": "NONE",
    }

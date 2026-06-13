"""
Guard Manager — Runs all 3 security guards on every vendor response.
Aggregates results and triggers human intervention if any guard fires.
"""

from guards import privacy_sentry, task_navigator, prompt_sanitizer


def analyze(vendor_response: str) -> dict:
    """
    Run all 3 guards on a vendor response and aggregate results.

    Args:
        vendor_response: The text of the vendor's message.

    Returns:
        {
            "safe": bool,          # True only if ALL guards passed
            "threats": [...],      # List of threat objects (guards that fired)
            "all_results": [...]   # All 3 guard results regardless
        }
    """
    results = [
        privacy_sentry.analyze(vendor_response),
        task_navigator.analyze(vendor_response),
        prompt_sanitizer.analyze(vendor_response),
    ]

    threats = [r for r in results if not r["safe"]]
    is_safe = len(threats) == 0

    return {
        "safe": is_safe,
        "threats": threats,
        "all_results": results,
    }


def human_intervention(vendor_name: str, threats: list[dict]) -> dict:
    """
    Present a security alert for human review and return the decision
    details (actual ALLOW/BLOCK decision is made by the frontend/API).

    Args:
        vendor_name: Name of the vendor that triggered the alert.
        threats: List of threat objects from guards that fired.

    Returns:
        {
            "vendor_name": str,
            "alert_message": str,
            "threats": [...],
            "max_severity": str,    # Highest severity across all threats
            "action_required": True
        }
    """
    # Determine highest severity
    severity_order = {"CRITICAL": 3, "HIGH": 2, "MEDIUM": 1, "NONE": 0}
    max_severity = "NONE"
    for threat in threats:
        if severity_order.get(threat["severity"], 0) > severity_order.get(max_severity, 0):
            max_severity = threat["severity"]

    # Build human-readable alert
    alert_lines = [
        f"🚨 SECURITY ALERT — Vendor: {vendor_name}",
        f"   Severity: {max_severity}",
        "",
    ]
    for i, threat in enumerate(threats, 1):
        alert_lines.append(f"   [{i}] Guard: {threat['guard']}")
        alert_lines.append(f"       Reason: {threat['reason']}")
        alert_lines.append(f"       Severity: {threat['severity']}")
        alert_lines.append("")

    alert_lines.append("   Action required: ALLOW or BLOCK this vendor?")
    alert_message = "\n".join(alert_lines)

    return {
        "vendor_name": vendor_name,
        "alert_message": alert_message,
        "threats": threats,
        "max_severity": max_severity,
        "action_required": True,
    }

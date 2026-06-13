"""
User Twin Agent — Represents the customer.
Selects the most relevant restaurant based on the user's food request
using keyword matching first, then AI-based selection as fallback.
Does NOT know which vendors are malicious.
"""

import re
from utils.ai_client import call_llm


# ---------- vendor registry (honest + malicious, twin doesn't know the difference) ----------
VENDOR_CATALOG = {
    "Pizza Palace": {
        "keywords": ["pizza", "pasta", "italian", "salad"],
        "cuisine": "Italian",
    },
    "Burger Barn": {
        "keywords": ["burger", "fries", "american", "milkshake"],
        "cuisine": "American",
    },
    "Sushi Express": {
        "keywords": ["sushi", "japanese", "roll", "avocado", "fish", "bento"],
        "cuisine": "Japanese",
    },
    "Phish & Chips": {
        "keywords": ["chips", "fish and chips", "fish", "british"],
        "cuisine": "British",
    },
    "Data Harvesters": {
        "keywords": ["healthy", "salad", "data", "greens"],
        "cuisine": "Health Food",
    },
    "Crypto Chips Co": {
        "keywords": ["crypto", "nachos", "snacks", "tortilla"],
        "cuisine": "Mexican / Snacks",
    },
}


def extract_price_limit(user_input: str) -> float | None:
    """
    Extract a price limit from phrases like "under $13", "below 20",
    "less than $15", "max 10", "budget 25", etc.
    Returns None if no price constraint is found.
    """
    patterns = [
        r"under\s*\$?\s*(\d+(?:\.\d+)?)",
        r"below\s*\$?\s*(\d+(?:\.\d+)?)",
        r"less\s+than\s*\$?\s*(\d+(?:\.\d+)?)",
        r"max(?:imum)?\s*\$?\s*(\d+(?:\.\d+)?)",
        r"budget\s*(?:of|is)?\s*\$?\s*(\d+(?:\.\d+)?)",
        r"\$\s*(\d+(?:\.\d+)?)\s*(?:limit|max|budget)",
    ]
    for pattern in patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def _keyword_match(user_input: str, excluded_vendors: list[str]) -> str | None:
    """
    Try to match the user's request to a vendor using keyword matching.
    Returns the vendor name or None if no match.
    """
    text = user_input.lower()

    # Check multi-word keywords first (e.g. "fish and chips")
    for vendor_name, info in VENDOR_CATALOG.items():
        if vendor_name in excluded_vendors:
            continue
        for kw in sorted(info["keywords"], key=len, reverse=True):
            if kw in text:
                return vendor_name
    return None


async def _llm_match(user_input: str, excluded_vendors: list[str]) -> str:
    """
    Fallback: ask the LLM to pick the best vendor from the available list.
    """
    available = {
        name: info["cuisine"]
        for name, info in VENDOR_CATALOG.items()
        if name not in excluded_vendors
    }

    if not available:
        return "No vendors available"

    vendor_list = "\n".join(
        f"- {name} ({cuisine})" for name, cuisine in available.items()
    )

    prompt = (
        f"A customer said: \"{user_input}\"\n\n"
        f"Available restaurants:\n{vendor_list}\n\n"
        f"Which ONE restaurant is the best match? "
        f"Reply with ONLY the restaurant name, nothing else."
    )

    response = await call_llm(prompt)
    response = response.strip().strip('"').strip("'")

    # Validate the LLM picked a real, non-excluded vendor
    for name in available:
        if name.lower() in response.lower():
            return name

    # If LLM returned garbage, pick the first available vendor
    return list(available.keys())[0]


async def select_vendor(
    user_input: str,
    excluded_vendors: list[str] | None = None,
) -> dict:
    """
    Main entry point for the User Twin Agent.

    Returns:
        {
            "vendor_name": str,
            "price_limit": float | None,
        }
    """
    excluded = excluded_vendors or []

    # Step 1 — extract price constraint
    price_limit = extract_price_limit(user_input)

    # Step 2 — keyword matching
    vendor = _keyword_match(user_input, excluded)

    # Step 3 — LLM fallback
    if vendor is None:
        vendor = await _llm_match(user_input, excluded)

    return {
        "vendor_name": vendor,
        "price_limit": price_limit,
    }

"""
Merchant normalization — maps raw receiver strings to a canonical merchant name.
Handles common variations like "AMZN PAY INDIA", "Amazon Seller Services", "Amazon UPI" → "amazon".
"""

import re

# Map of normalized name → list of regex patterns that match raw receiver strings
MERCHANT_MAP: dict[str, list[re.Pattern]] = {
    "amazon": [
        re.compile(r"\bamazon\b", re.IGNORECASE),
        re.compile(r"\bamzn\b", re.IGNORECASE),
    ],
    "flipkart": [
        re.compile(r"\bflipkart\b", re.IGNORECASE),
        re.compile(r"\bfk\b", re.IGNORECASE),
    ],
    "swiggy": [
        re.compile(r"\bswiggy\b", re.IGNORECASE),
    ],
    "zomato": [
        re.compile(r"\bzomato\b", re.IGNORECASE),
    ],
    "netflix": [
        re.compile(r"\bnetflix\b", re.IGNORECASE),
    ],
    "spotify": [
        re.compile(r"\bspotify\b", re.IGNORECASE),
    ],
    "youtube": [
        re.compile(r"\byoutube\b", re.IGNORECASE),
        re.compile(r"\byt\s*premium\b", re.IGNORECASE),
    ],
    "hotstar": [
        re.compile(r"\bhotstar\b", re.IGNORECASE),
        re.compile(r"\bdisney\+?\s*hotstar\b", re.IGNORECASE),
    ],
    "uber": [
        re.compile(r"\buber\b", re.IGNORECASE),
    ],
    "ola": [
        re.compile(r"\bola\b", re.IGNORECASE),
    ],
    "rapido": [
        re.compile(r"\brapido\b", re.IGNORECASE),
    ],
    "phonepe": [
        re.compile(r"\bphonepe\b", re.IGNORECASE),
        re.compile(r"\bphone\s*pe\b", re.IGNORECASE),
    ],
    "paytm": [
        re.compile(r"\bpaytm\b", re.IGNORECASE),
    ],
    "gpay": [
        re.compile(r"\bgpay\b", re.IGNORECASE),
        re.compile(r"\bgoogle\s*pay\b", re.IGNORECASE),
    ],
    "blinkit": [
        re.compile(r"\bblinkit\b", re.IGNORECASE),
        re.compile(r"\bgrofers\b", re.IGNORECASE),
    ],
    "bigbasket": [
        re.compile(r"\bbigbasket\b", re.IGNORECASE),
        re.compile(r"\bbig\s*basket\b", re.IGNORECASE),
    ],
    "dunzo": [
        re.compile(r"\bdunzo\b", re.IGNORECASE),
    ],
    "zepto": [
        re.compile(r"\bzepto\b", re.IGNORECASE),
    ],
    "myntra": [
        re.compile(r"\bmyntra\b", re.IGNORECASE),
    ],
    "nykaa": [
        re.compile(r"\bnykaa\b", re.IGNORECASE),
    ],
    "meesho": [
        re.compile(r"\bmeesho\b", re.IGNORECASE),
    ],
    "irctc": [
        re.compile(r"\birctc\b", re.IGNORECASE),
    ],
    "makemytrip": [
        re.compile(r"\bmakemytrip\b", re.IGNORECASE),
        re.compile(r"\bmmt\b", re.IGNORECASE),
    ],
    "goibibo": [
        re.compile(r"\bgoibibo\b", re.IGNORECASE),
    ],
    "airtel": [
        re.compile(r"\bairtel\b", re.IGNORECASE),
    ],
    "jio": [
        re.compile(r"\bjio\b", re.IGNORECASE),
        re.compile(r"\breliance\s*jio\b", re.IGNORECASE),
    ],
    "bsnl": [
        re.compile(r"\bbsnl\b", re.IGNORECASE),
    ],
    "vi": [
        re.compile(r"\bvodafone\b", re.IGNORECASE),
        re.compile(r"\bidea\b", re.IGNORECASE),
        re.compile(r"\bvi\b", re.IGNORECASE),
    ],
    "hdfc": [
        re.compile(r"\bhdfc\b", re.IGNORECASE),
    ],
    "icici": [
        re.compile(r"\bicici\b", re.IGNORECASE),
    ],
    "sbi": [
        re.compile(r"\bsbi\b", re.IGNORECASE),
        re.compile(r"\bstate\s*bank\b", re.IGNORECASE),
    ],
    "axis": [
        re.compile(r"\baxis\s*bank\b", re.IGNORECASE),
    ],
    "lenskart": [
        re.compile(r"\blenskart\b", re.IGNORECASE),
    ],
    "cult_fit": [
        re.compile(r"\bcult\.?fit\b", re.IGNORECASE),
        re.compile(r"\bcure\.?fit\b", re.IGNORECASE),
    ],
}


def normalize_merchant(raw_receiver: str) -> str:
    """
    Returns a normalized merchant name for a raw receiver string.
    Falls back to a lowercased, stripped version of the raw string if no match found.
    """
    if not raw_receiver:
        return "unknown"

    text = raw_receiver.strip()
    for merchant, patterns in MERCHANT_MAP.items():
        for pattern in patterns:
            if pattern.search(text):
                return merchant

    # Fallback: lowercase and strip special chars for a clean canonical form
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", text).strip().lower()
    # Collapse whitespace
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned or "unknown"

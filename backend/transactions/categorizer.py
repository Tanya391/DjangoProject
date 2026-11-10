"""
Hybrid transaction categorizer.
Combines regex pattern matching + merchant-to-category mapping to assign
one of the supported fine-grained categories to a transaction.

Supported categories:
    groceries, food_delivery, utilities, subscriptions, rent, emi,
    travel, medical, fuel, shopping, entertainment, salary, investment,
    insurance, internet, electricity, income, other
"""

import re
from .merchant_normalizer import normalize_merchant

# ---------------------------------------------------------------------------
# Merchant → category overrides (checked first, highest priority)
# ---------------------------------------------------------------------------
MERCHANT_CATEGORY_MAP: dict[str, str] = {
    "netflix": "subscriptions",
    "spotify": "subscriptions",
    "youtube": "subscriptions",
    "hotstar": "subscriptions",
    "amazon": "shopping",
    "flipkart": "shopping",
    "myntra": "shopping",
    "nykaa": "shopping",
    "meesho": "shopping",
    "swiggy": "food_delivery",
    "zomato": "food_delivery",
    "dunzo": "groceries",
    "blinkit": "groceries",
    "bigbasket": "groceries",
    "zepto": "groceries",
    "uber": "travel",
    "ola": "travel",
    "rapido": "travel",
    "irctc": "travel",
    "makemytrip": "travel",
    "goibibo": "travel",
    "airtel": "internet",
    "jio": "internet",
    "bsnl": "internet",
    "vi": "internet",
    "cult_fit": "medical",
    "lenskart": "medical",
    "phonepe": "other",
    "paytm": "other",
    "gpay": "other",
}

# ---------------------------------------------------------------------------
# Regex patterns per category (checked after merchant map)
# ---------------------------------------------------------------------------
CATEGORY_PATTERNS: dict[str, list[re.Pattern]] = {
    "salary": [
        re.compile(r"\bsalary\b", re.IGNORECASE),
        re.compile(r"\bpayroll\b", re.IGNORECASE),
        re.compile(r"\bstipend\b", re.IGNORECASE),
    ],
    "income": [
        re.compile(r"\bbonus\b", re.IGNORECASE),
        re.compile(r"\brefund\b", re.IGNORECASE),
        re.compile(r"\binterest\b", re.IGNORECASE),
        re.compile(r"\bdividend\b", re.IGNORECASE),
        re.compile(r"\bcashback\b", re.IGNORECASE),
        re.compile(r"\breward\b", re.IGNORECASE),
    ],
    "investment": [
        re.compile(r"\bmutual\s*fund\b", re.IGNORECASE),
        re.compile(r"\bsip\b", re.IGNORECASE),
        re.compile(r"\bzerodha\b", re.IGNORECASE),
        re.compile(r"\bgroww\b", re.IGNORECASE),
        re.compile(r"\bupstox\b", re.IGNORECASE),
        re.compile(r"\bstock\b", re.IGNORECASE),
        re.compile(r"\bdemat\b", re.IGNORECASE),
        re.compile(r"\bnps\b", re.IGNORECASE),
        re.compile(r"\bppf\b", re.IGNORECASE),
        re.compile(r"\bfd\b", re.IGNORECASE),
    ],
    "rent": [
        re.compile(r"\brent\b", re.IGNORECASE),
        re.compile(r"\bhouse\s*rent\b", re.IGNORECASE),
        re.compile(r"\bpg\b", re.IGNORECASE),
        re.compile(r"\bhostel\b", re.IGNORECASE),
    ],
    "emi": [
        re.compile(r"\bemi\b", re.IGNORECASE),
        re.compile(r"\bloan\b", re.IGNORECASE),
        re.compile(r"\brepayment\b", re.IGNORECASE),
        re.compile(r"\binstalment\b", re.IGNORECASE),
        re.compile(r"\binstallment\b", re.IGNORECASE),
    ],
    "insurance": [
        re.compile(r"\binsurance\b", re.IGNORECASE),
        re.compile(r"\bpremium\b", re.IGNORECASE),
        re.compile(r"\blic\b", re.IGNORECASE),
        re.compile(r"\bpolicy\b", re.IGNORECASE),
    ],
    "electricity": [
        re.compile(r"\belectricity\b", re.IGNORECASE),
        re.compile(r"\bpower\s*bill\b", re.IGNORECASE),
        re.compile(r"\bescom\b", re.IGNORECASE),
        re.compile(r"\bbescom\b", re.IGNORECASE),
        re.compile(r"\btorrent\s*power\b", re.IGNORECASE),
        re.compile(r"\bmsedcl\b", re.IGNORECASE),
    ],
    "utilities": [
        re.compile(r"\bwater\b", re.IGNORECASE),
        re.compile(r"\bgas\b", re.IGNORECASE),
        re.compile(r"\bindane\b", re.IGNORECASE),
        re.compile(r"\bhp\s*gas\b", re.IGNORECASE),
        re.compile(r"\bbharat\s*gas\b", re.IGNORECASE),
        re.compile(r"\bpiped\s*gas\b", re.IGNORECASE),
        re.compile(r"\bmunicipal\b", re.IGNORECASE),
    ],
    "internet": [
        re.compile(r"\binternet\b", re.IGNORECASE),
        re.compile(r"\bbroadband\b", re.IGNORECASE),
        re.compile(r"\bwifi\b", re.IGNORECASE),
        re.compile(r"\bmobile\s*recharge\b", re.IGNORECASE),
        re.compile(r"\brecharge\b", re.IGNORECASE),
        re.compile(r"\bprepaid\b", re.IGNORECASE),
        re.compile(r"\bpostpaid\b", re.IGNORECASE),
    ],
    "groceries": [
        re.compile(r"\bgrocery\b", re.IGNORECASE),
        re.compile(r"\bgroceries\b", re.IGNORECASE),
        re.compile(r"\bsupermarket\b", re.IGNORECASE),
        re.compile(r"\breliance\s*fresh\b", re.IGNORECASE),
        re.compile(r"\bdmart\b", re.IGNORECASE),
        re.compile(r"\bmore\s*supermarket\b", re.IGNORECASE),
        re.compile(r"\bspencer\b", re.IGNORECASE),
        re.compile(r"\bnature'?s\s*basket\b", re.IGNORECASE),
    ],
    "food_delivery": [
        re.compile(r"\brestaurant\b", re.IGNORECASE),
        re.compile(r"\bcafe\b", re.IGNORECASE),
        re.compile(r"\bfood\b", re.IGNORECASE),
        re.compile(r"\bdining\b", re.IGNORECASE),
        re.compile(r"\bpizza\b", re.IGNORECASE),
        re.compile(r"\bburger\b", re.IGNORECASE),
        re.compile(r"\bbiryani\b", re.IGNORECASE),
    ],
    "fuel": [
        re.compile(r"\bfuel\b", re.IGNORECASE),
        re.compile(r"\bpetrol\b", re.IGNORECASE),
        re.compile(r"\bdiesel\b", re.IGNORECASE),
        re.compile(r"\bhpcl\b", re.IGNORECASE),
        re.compile(r"\bbpcl\b", re.IGNORECASE),
        re.compile(r"\biocl\b", re.IGNORECASE),
        re.compile(r"\bgas\s*station\b", re.IGNORECASE),
    ],
    "travel": [
        re.compile(r"\bflight\b", re.IGNORECASE),
        re.compile(r"\bairline\b", re.IGNORECASE),
        re.compile(r"\btrain\b", re.IGNORECASE),
        re.compile(r"\bbus\b", re.IGNORECASE),
        re.compile(r"\bhotel\b", re.IGNORECASE),
        re.compile(r"\btaxi\b", re.IGNORECASE),
        re.compile(r"\bcab\b", re.IGNORECASE),
        re.compile(r"\bauto\b", re.IGNORECASE),
        re.compile(r"\bmetro\b", re.IGNORECASE),
    ],
    "medical": [
        re.compile(r"\bhospital\b", re.IGNORECASE),
        re.compile(r"\bclinic\b", re.IGNORECASE),
        re.compile(r"\bpharmacy\b", re.IGNORECASE),
        re.compile(r"\bmedicine\b", re.IGNORECASE),
        re.compile(r"\bdoctor\b", re.IGNORECASE),
        re.compile(r"\blab\s*test\b", re.IGNORECASE),
        re.compile(r"\bdiagnostic\b", re.IGNORECASE),
        re.compile(r"\bmedical\b", re.IGNORECASE),
        re.compile(r"\bapollo\b", re.IGNORECASE),
        re.compile(r"\bnetmeds\b", re.IGNORECASE),
        re.compile(r"\b1mg\b", re.IGNORECASE),
        re.compile(r"\bpharmaeasy\b", re.IGNORECASE),
    ],
    "entertainment": [
        re.compile(r"\bmovie\b", re.IGNORECASE),
        re.compile(r"\bcinema\b", re.IGNORECASE),
        re.compile(r"\bpvr\b", re.IGNORECASE),
        re.compile(r"\binox\b", re.IGNORECASE),
        re.compile(r"\bgaming\b", re.IGNORECASE),
        re.compile(r"\bgame\b", re.IGNORECASE),
        re.compile(r"\bconcert\b", re.IGNORECASE),
        re.compile(r"\bevent\b", re.IGNORECASE),
        re.compile(r"\bticket\b", re.IGNORECASE),
        re.compile(r"\bbookmyshow\b", re.IGNORECASE),
    ],
    "shopping": [
        re.compile(r"\bshopping\b", re.IGNORECASE),
        re.compile(r"\bclothes\b", re.IGNORECASE),
        re.compile(r"\bfashion\b", re.IGNORECASE),
        re.compile(r"\belectronics\b", re.IGNORECASE),
        re.compile(r"\bgadget\b", re.IGNORECASE),
    ],
    "subscriptions": [
        re.compile(r"\bsubscription\b", re.IGNORECASE),
        re.compile(r"\bmonthly\s*plan\b", re.IGNORECASE),
        re.compile(r"\bannual\s*plan\b", re.IGNORECASE),
        re.compile(r"\bmembership\b", re.IGNORECASE),
    ],
}

# Priority order — first match wins
CATEGORY_PRIORITY = [
    "salary",
    "income",
    "investment",
    "rent",
    "emi",
    "insurance",
    "electricity",
    "utilities",
    "internet",
    "subscriptions",
    "groceries",
    "food_delivery",
    "fuel",
    "travel",
    "medical",
    "entertainment",
    "shopping",
]


def categorize_transaction(receiver: str, description: str, transaction_type: str) -> str:
    """
    Returns a fine-grained category string for a transaction.
    Priority:
      1. Merchant map (normalized merchant → category)
      2. Regex patterns on combined receiver + description text
      3. Credit transactions default to 'income'
      4. Fallback: 'other'
    """
    normalized = normalize_merchant(receiver)

    # 1. Merchant map
    if normalized in MERCHANT_CATEGORY_MAP:
        return MERCHANT_CATEGORY_MAP[normalized]

    combined = f"{receiver} {description}"

    # 2. Regex patterns in priority order
    for category in CATEGORY_PRIORITY:
        patterns = CATEGORY_PATTERNS.get(category, [])
        for pattern in patterns:
            if pattern.search(combined):
                return category

    # 3. Credit default
    if transaction_type == "credit":
        return "income"

    return "other"

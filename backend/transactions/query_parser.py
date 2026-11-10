"""
Query Understanding Layer — converts natural language into structured financial intent.

Extracts:
  - intent: what the user wants (sum, list, trend, compare, explain, subscription)
  - category: spending category if mentioned
  - merchant: normalized merchant name if mentioned
  - date_from / date_to: date range
  - transaction_type: debit / credit / None
  - aggregation: sum / average / count / None
  - raw_query: original question

Uses regex + dateparser for lightweight, dependency-minimal extraction.
"""

import re
from datetime import date, timedelta
from calendar import monthrange
from typing import Literal

from pydantic import BaseModel

try:
    import dateparser
    _DATEPARSER_AVAILABLE = True
except ImportError:
    _DATEPARSER_AVAILABLE = False

from .merchant_normalizer import MERCHANT_MAP
from .categorizer import CATEGORY_PATTERNS

# ---------------------------------------------------------------------------
# Intent patterns
# ---------------------------------------------------------------------------
INTENT_PATTERNS: list[tuple[str, list[re.Pattern]]] = [
    ("explain", [
        re.compile(r"\bwhy\b", re.IGNORECASE),
        re.compile(r"\bexplain\b", re.IGNORECASE),
        re.compile(r"\bwhat\s+is\b", re.IGNORECASE),
        re.compile(r"\btell\s+me\s+about\b", re.IGNORECASE),
        re.compile(r"\bpattern", re.IGNORECASE),
        re.compile(r"\bhow\s+can\s+i\b", re.IGNORECASE),
    ]),
    ("sum_expenses", [
        re.compile(r"\bhow\s+much\b.*\bspend\b", re.IGNORECASE),
        re.compile(r"\btotal\b.*\bspend\b", re.IGNORECASE),
        re.compile(r"\bspent\b", re.IGNORECASE),
        re.compile(r"\bexpenses?\b", re.IGNORECASE),
        re.compile(r"\bsum\b", re.IGNORECASE),
    ]),
    ("list_transactions", [
        re.compile(r"\bshow\b", re.IGNORECASE),
        re.compile(r"\blist\b", re.IGNORECASE),
        re.compile(r"\bfetch\b", re.IGNORECASE),
        re.compile(r"\bget\b.*\btransaction", re.IGNORECASE),
        re.compile(r"\brecent\b", re.IGNORECASE),
        re.compile(r"\blast\s+\d+\b", re.IGNORECASE),
    ]),
    ("trend_analysis", [
        re.compile(r"\btrend\b", re.IGNORECASE),
        re.compile(r"\bover\s+time\b", re.IGNORECASE),
        re.compile(r"\bmonth\s+by\s+month\b", re.IGNORECASE),
        re.compile(r"\bincreased?\b", re.IGNORECASE),
        re.compile(r"\bdecreased?\b", re.IGNORECASE),
        re.compile(r"\bchanged?\b", re.IGNORECASE),
    ]),
    ("compare_periods", [
        re.compile(r"\bcompare\b", re.IGNORECASE),
        re.compile(r"\bvs\.?\b", re.IGNORECASE),
        re.compile(r"\bversus\b", re.IGNORECASE),
        re.compile(r"\blast\s+month\b.*\bthis\s+month\b", re.IGNORECASE),
        re.compile(r"\bthis\s+month\b.*\blast\s+month\b", re.IGNORECASE),
    ]),
    ("cashflow", [
        re.compile(r"\bcash\s*flow\b", re.IGNORECASE),
        re.compile(r"\bincome\s+vs\b", re.IGNORECASE),
        re.compile(r"\bnet\s+balance\b", re.IGNORECASE),
        re.compile(r"\bhow\s+much\b.*\bearned?\b", re.IGNORECASE),
        re.compile(r"\bhow\s+much\b.*\breceived?\b", re.IGNORECASE),
    ]),
    ("subscription_check", [
        re.compile(r"\bsubscription\b", re.IGNORECASE),
        re.compile(r"\brecurring\b", re.IGNORECASE),
        re.compile(r"\bmonthly\s+charge\b", re.IGNORECASE),
    ]),
]

# ---------------------------------------------------------------------------
# Date range helpers
# ---------------------------------------------------------------------------
_MONTH_NAMES = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

_THIS_MONTH_PATTERN = re.compile(r"\bthis\s+month\b", re.IGNORECASE)
_LAST_MONTH_PATTERN = re.compile(r"\blast\s+month\b", re.IGNORECASE)
_THIS_YEAR_PATTERN = re.compile(r"\bthis\s+year\b", re.IGNORECASE)
_LAST_YEAR_PATTERN = re.compile(r"\blast\s+year\b", re.IGNORECASE)
_LAST_N_DAYS_PATTERN = re.compile(r"\blast\s+(\d+)\s+days?\b", re.IGNORECASE)
_LAST_N_MONTHS_PATTERN = re.compile(r"\blast\s+(\d+)\s+months?\b", re.IGNORECASE)
_NAMED_MONTH_PATTERN = re.compile(
    r"\b(january|february|march|april|may|june|july|august|september|october|november|december"
    r"|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\b",
    re.IGNORECASE,
)


def _month_range(year: int, month: int) -> tuple[date, date]:
    last_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def _extract_date_range(text: str) -> tuple[date | None, date | None]:
    today = date.today()

    if _THIS_MONTH_PATTERN.search(text):
        return _month_range(today.year, today.month)

    if _LAST_MONTH_PATTERN.search(text):
        first_of_this = today.replace(day=1)
        last_month_end = first_of_this - timedelta(days=1)
        return _month_range(last_month_end.year, last_month_end.month)

    if _THIS_YEAR_PATTERN.search(text):
        return date(today.year, 1, 1), date(today.year, 12, 31)

    if _LAST_YEAR_PATTERN.search(text):
        return date(today.year - 1, 1, 1), date(today.year - 1, 12, 31)

    m = _LAST_N_DAYS_PATTERN.search(text)
    if m:
        n = int(m.group(1))
        return today - timedelta(days=n), today

    m = _LAST_N_MONTHS_PATTERN.search(text)
    if m:
        n = int(m.group(1))
        start = today - timedelta(days=n * 30)
        return start, today

    # Check for explicit 4-digit year in the text (e.g. "february 2024")
    year_match = re.search(r'\b(20\d{2})\b', text)

    m = _NAMED_MONTH_PATTERN.search(text)
    if m:
        month_num = _MONTH_NAMES[m.group(1).lower()]
        if year_match:
            # Explicit year provided — use it directly
            year = int(year_match.group(1))
        else:
            # No explicit year — find the most recent year that has data
            # for this month by querying MongoDB
            year = _find_year_with_data(month_num) or today.year
        return _month_range(year, month_num)

    return None, None


def _find_year_with_data(month_num: int) -> int | None:
    """
    Query MongoDB to find the most recent year that has transactions
    in the given month number. Falls back to None if DB is unreachable.
    """
    try:
        from .utils import get_db
        from django.conf import settings
        db = get_db()
        col = db[settings.MONGO_TRANSACTIONS_COLLECTION]
        month_str = f"-{month_num:02d}-"
        # Find the most recent document whose date contains this month
        doc = col.find_one(
            {"date": {"$regex": month_str}},
            {"date": 1, "_id": 0},
            sort=[("date", -1)],
        )
        if doc and doc.get("date"):
            return int(doc["date"][:4])
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Category extraction
# ---------------------------------------------------------------------------
def _extract_category(text: str) -> str | None:
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(text):
                return category
    return None


# ---------------------------------------------------------------------------
# Merchant extraction
# ---------------------------------------------------------------------------
def _extract_merchant(text: str) -> str | None:
    for merchant, patterns in MERCHANT_MAP.items():
        for pattern in patterns:
            if pattern.search(text):
                return merchant
    return None


# ---------------------------------------------------------------------------
# Transaction type extraction
# ---------------------------------------------------------------------------
_DEBIT_PATTERN = re.compile(r"\b(debit|spent|paid|expense|purchase|bought)\b", re.IGNORECASE)
_CREDIT_PATTERN = re.compile(r"\b(credit|income|received|earned|salary|refund)\b", re.IGNORECASE)


def _extract_transaction_type(text: str) -> str | None:
    if _CREDIT_PATTERN.search(text):
        return "credit"
    if _DEBIT_PATTERN.search(text):
        return "debit"
    return None


# ---------------------------------------------------------------------------
# Aggregation extraction
# ---------------------------------------------------------------------------
_AVG_PATTERN = re.compile(r"\b(average|avg|mean)\b", re.IGNORECASE)
_COUNT_PATTERN = re.compile(r"\b(how\s+many|count|number\s+of)\b", re.IGNORECASE)


def _extract_aggregation(text: str) -> str | None:
    if _AVG_PATTERN.search(text):
        return "average"
    if _COUNT_PATTERN.search(text):
        return "count"
    # Default for sum_expenses intent
    return None


# ---------------------------------------------------------------------------
# Intent extraction
# ---------------------------------------------------------------------------
def _extract_intent(text: str) -> str:
    for intent, patterns in INTENT_PATTERNS:
        for pattern in patterns:
            if pattern.search(text):
                return intent
    return "semantic_search"  # default — use deterministic retrieval


# ---------------------------------------------------------------------------
# Public schema + parser
# ---------------------------------------------------------------------------
class ParsedQuery(BaseModel):
    intent: str
    category: str | None = None
    merchant: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    transaction_type: str | None = None
    aggregation: str | None = None
    raw_query: str

    class Config:
        json_encoders = {date: lambda v: v.isoformat()}


def parse_query(question: str) -> ParsedQuery:
    """
    Parse a natural language financial question into a structured ParsedQuery.
    """
    text = (question or "").strip()

    intent = _extract_intent(text)
    category = _extract_category(text)
    merchant = _extract_merchant(text)
    date_from, date_to = _extract_date_range(text)
    transaction_type = _extract_transaction_type(text)
    aggregation = _extract_aggregation(text)

    # If intent is sum_expenses and no explicit aggregation, default to sum
    if intent == "sum_expenses" and aggregation is None:
        aggregation = "sum"

    return ParsedQuery(
        intent=intent,
        category=category,
        merchant=merchant,
        date_from=date_from,
        date_to=date_to,
        transaction_type=transaction_type,
        aggregation=aggregation,
        raw_query=text,
    )

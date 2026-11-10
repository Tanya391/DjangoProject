"""
Deterministic Analytics Engine powered by Django ORM.

Demonstrates core Django ORM capabilities:
  - QuerySet filtering and Q objects
  - ORM Aggregation & Annotation (Sum, Count, TruncMonth)
  - Ordering and slicing
  - Relational querying
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from datetime import date, datetime
from typing import Any

from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth

from .models import Transaction


def _base_qs(
    user_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    transaction_type: str | None = None,
    category: str | None = None,
):
    qs = Transaction.objects.all()

    if user_id:
        try:
            uid = int(user_id)
            qs = qs.filter(Q(user_id=uid) | Q(user__isnull=True))
        except (ValueError, TypeError):
            qs = qs.filter(user__isnull=True)

    if transaction_type:
        qs = qs.filter(transaction_type=transaction_type)

    if category:
        qs = qs.filter(category_name__icontains=category)

    if date_from:
        qs = qs.filter(date__gte=date_from)

    if date_to:
        qs = qs.filter(date__lte=date_to)

    return qs


# ---------------------------------------------------------------------------
# Total spending (Django ORM Sum & Count)
# ---------------------------------------------------------------------------
def get_total_spending(
    user_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    category: str | None = None,
    transaction_type: str = "debit",
) -> dict[str, Any]:
    qs = _base_qs(user_id, date_from, date_to, transaction_type, category)
    agg = qs.aggregate(total=Sum("amount"), count=Count("id"))
    total_val = float(agg["total"]) if agg["total"] is not None else 0.0
    return {"total": round(total_val, 2), "count": agg["count"] or 0}


# ---------------------------------------------------------------------------
# Monthly summary (Django ORM TruncMonth)
# ---------------------------------------------------------------------------
def get_monthly_summary(
    user_id: str | None = None,
    year: int | None = None,
) -> list[dict[str, Any]]:
    qs = Transaction.objects.all()
    if user_id:
        try:
            uid = int(user_id)
            qs = qs.filter(Q(user_id=uid) | Q(user__isnull=True))
        except (ValueError, TypeError):
            qs = qs.filter(user__isnull=True)

    if year:
        qs = qs.filter(date__year=year)

    rows = (
        qs.annotate(month=TruncMonth("date"))
        .values("month", "transaction_type")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("month")
    )

    summary: dict[str, dict] = defaultdict(lambda: {"income": 0.0, "expense": 0.0, "count": 0})
    for row in rows:
        m_val = row["month"]
        if not m_val:
            continue
        ym = m_val.strftime("%Y-%m")
        t = row["transaction_type"]
        val = float(row["total"] or 0.0)
        cnt = row["count"] or 0

        if t == "credit":
            summary[ym]["income"] += val
        else:
            summary[ym]["expense"] += val
        summary[ym]["count"] += cnt

    result = []
    for ym, data in sorted(summary.items()):
        result.append({
            "month": ym,
            "income": round(data["income"], 2),
            "expense": round(data["expense"], 2),
            "net": round(data["income"] - data["expense"], 2),
            "count": data["count"],
        })
    return result


# ---------------------------------------------------------------------------
# Category breakdown (Django ORM Group By & Ordering)
# ---------------------------------------------------------------------------
def get_category_breakdown(
    user_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    transaction_type: str = "debit",
) -> list[dict[str, Any]]:
    qs = _base_qs(user_id, date_from, date_to, transaction_type)
    rows = (
        qs.values("category_name")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("-total")
    )

    return [
        {
            "category": r["category_name"] or "other",
            "total": round(float(r["total"] or 0.0), 2),
            "count": r["count"] or 0,
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Top merchants (Django ORM Aggregation & Slicing)
# ---------------------------------------------------------------------------
def get_top_merchants(
    user_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 10,
    transaction_type: str = "debit",
) -> list[dict[str, Any]]:
    qs = _base_qs(user_id, date_from, date_to, transaction_type)
    rows = (
        qs.values("normalized_merchant")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("-total")[:limit]
    )

    return [
        {
            "merchant": r["normalized_merchant"] or "unknown",
            "total": round(float(r["total"] or 0.0), 2),
            "count": r["count"] or 0,
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Cashflow (Django ORM Conditional Aggregations)
# ---------------------------------------------------------------------------
def get_cashflow(
    user_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> dict[str, Any]:
    qs = _base_qs(user_id, date_from, date_to)

    credit_agg = qs.filter(transaction_type="credit").aggregate(total=Sum("amount"), count=Count("id"))
    debit_agg = qs.filter(transaction_type="debit").aggregate(total=Sum("amount"), count=Count("id"))

    income = float(credit_agg["total"] or 0.0)
    expense = float(debit_agg["total"] or 0.0)

    return {
        "income": round(income, 2),
        "expense": round(expense, 2),
        "net": round(income - expense, 2),
        "income_count": credit_agg["count"] or 0,
        "expense_count": debit_agg["count"] or 0,
    }


# ---------------------------------------------------------------------------
# Subscription detection (Django ORM Grouping & statistical detection)
# ---------------------------------------------------------------------------
def detect_subscriptions(
    user_id: str | None = None,
    min_occurrences: int = 2,
) -> list[dict[str, Any]]:
    qs = _base_qs(user_id, transaction_type="debit")
    merchants_summary = (
        qs.values("normalized_merchant")
        .annotate(occurrences=Count("id"), total=Sum("amount"))
        .filter(occurrences__gte=min_occurrences)
        .order_by("-occurrences")
    )

    subscriptions = []
    for item in merchants_summary:
        merchant = item["normalized_merchant"]
        if not merchant:
            continue
        txs = qs.filter(normalized_merchant=merchant).values_list("amount", "date")
        amounts = [float(t[0]) for t in txs]
        dates = [t[1].isoformat() if hasattr(t[1], "isoformat") else str(t[1]) for t in txs]

        if len(amounts) >= 2:
            mean_amt = statistics.mean(amounts)
            try:
                std_dev = statistics.stdev(amounts)
            except statistics.StatisticsError:
                std_dev = 0
            if mean_amt > 0 and (std_dev / mean_amt) < 0.25:
                subscriptions.append({
                    "merchant": merchant,
                    "occurrences": item["occurrences"],
                    "avg_amount": round(mean_amt, 2),
                    "total_charged": round(float(item["total"] or 0.0), 2),
                    "last_date": max(dates) if dates else None,
                })

    return subscriptions


# ---------------------------------------------------------------------------
# Period comparison (Django ORM date range comparisons)
# ---------------------------------------------------------------------------
def compare_months(
    user_id: str | None = None,
    period_a_from: date | None = None,
    period_a_to: date | None = None,
    period_b_from: date | None = None,
    period_b_to: date | None = None,
    category: str | None = None,
) -> dict[str, Any]:
    spend_a = get_total_spending(user_id=user_id, date_from=period_a_from, date_to=period_a_to, category=category)
    spend_b = get_total_spending(user_id=user_id, date_from=period_b_from, date_to=period_b_to, category=category)

    total_a = spend_a["total"]
    total_b = spend_b["total"]
    diff = round(total_b - total_a, 2)
    pct_change = round((diff / total_a * 100), 2) if total_a > 0 else 0.0

    return {
        "period_a": {"total": total_a, "count": spend_a["count"], "from": str(period_a_from), "to": str(period_a_to)},
        "period_b": {"total": total_b, "count": spend_b["count"], "from": str(period_b_from), "to": str(period_b_to)},
        "diff": diff,
        "percentage_change": pct_change,
        "trend": "increased" if diff > 0 else ("decreased" if diff < 0 else "neutral"),
    }


# ---------------------------------------------------------------------------
# Category trend analysis (Django ORM TruncMonth)
# ---------------------------------------------------------------------------
def category_trend_analysis(category: str, user_id: str | None = None) -> list[dict[str, Any]]:
    qs = _base_qs(user_id=user_id, category=category, transaction_type="debit")
    rows = (
        qs.annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("month")
    )

    trends = []
    for r in rows:
        m = r["month"]
        if not m:
            continue
        trends.append({
            "month": m.strftime("%Y-%m"),
            "category": category,
            "total": round(float(r["total"] or 0.0), 2),
            "count": r["count"],
        })
    return trends


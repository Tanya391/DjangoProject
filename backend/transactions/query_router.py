"""
Query Router — decides how to handle each query based on parsed intent.

Routing table:
  sum_expenses       → deterministic analytics (get_total_spending)
  list_transactions  → hybrid retrieval
  trend_analysis     → analytics (category_trend_analysis / monthly_summary)
  compare_periods    → analytics (compare_months)
  cashflow           → analytics (get_cashflow)
  subscription_check → analytics (detect_subscriptions)
  explain            → retrieval + LLM
  semantic_search    → hybrid retrieval + LLM
"""

from __future__ import annotations

import logging
from typing import Any

from .query_parser import ParsedQuery

logger = logging.getLogger(__name__)

# Route type constants
ROUTE_ANALYTICS = "analytics"
ROUTE_RETRIEVAL = "retrieval"
ROUTE_RAG = "rag"          # retrieval + LLM explanation
ROUTE_HYBRID = "hybrid"    # analytics + retrieval + LLM


INTENT_ROUTE_MAP: dict[str, str] = {
    "sum_expenses": ROUTE_ANALYTICS,
    "trend_analysis": ROUTE_ANALYTICS,
    "compare_periods": ROUTE_ANALYTICS,
    "cashflow": ROUTE_ANALYTICS,
    "subscription_check": ROUTE_ANALYTICS,
    "list_transactions": ROUTE_RETRIEVAL,
    "explain": ROUTE_RAG,
    "semantic_search": ROUTE_RAG,
}


def route_query(parsed: ParsedQuery) -> str:
    """
    Returns the route type for a parsed query.
    """
    route = INTENT_ROUTE_MAP.get(parsed.intent, ROUTE_RAG)
    logger.debug("Query routed: intent=%s → route=%s", parsed.intent, route)
    return route


def execute_analytics_route(parsed: ParsedQuery, user_id: str | None) -> dict[str, Any]:
    """
    Execute deterministic analytics based on parsed intent.
    Returns a structured result dict — no LLM involved.
    """
    from .analytics_service import (
        get_total_spending,
        get_monthly_summary,
        get_cashflow,
        detect_subscriptions,
        compare_months,
        category_trend_analysis,
    )

    intent = parsed.intent

    if intent == "sum_expenses":
        result = get_total_spending(
            user_id=user_id,
            date_from=parsed.date_from,
            date_to=parsed.date_to,
            category=parsed.category,
            transaction_type=parsed.transaction_type or "debit",
        )
        return {
            "route": ROUTE_ANALYTICS,
            "intent": intent,
            "data": result,
            "summary": (
                f"Total {parsed.category or 'spending'}: ₹{result['total']:,.2f} "
                f"across {result['count']} transaction(s)"
                + (f" from {parsed.date_from} to {parsed.date_to}" if parsed.date_from else "")
            ),
        }

    if intent == "trend_analysis":
        category = parsed.category or "other"
        result = category_trend_analysis(category=category, user_id=user_id)
        return {
            "route": ROUTE_ANALYTICS,
            "intent": intent,
            "category": category,
            "data": result,
        }

    if intent == "compare_periods":
        # Default: compare last month vs this month
        from datetime import date
        from calendar import monthrange

        today = date.today()
        this_month_start = today.replace(day=1)
        last_day_this = monthrange(today.year, today.month)[1]
        this_month_end = today.replace(day=last_day_this)

        prev_month_end = this_month_start.replace(day=1) - __import__("datetime").timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)

        # If the query mentions specific months, try to extract them from parsed
        if parsed.date_from and parsed.date_to:
            # Use the parsed date as period B, and the month before as period A
            import datetime as dt
            period_b_start = parsed.date_from
            period_b_end = parsed.date_to
            prev_end = period_b_start - dt.timedelta(days=1)
            prev_start = prev_end.replace(day=1)
            result = compare_months(
                user_id=user_id,
                period_a_from=prev_start,
                period_a_to=prev_end,
                period_b_from=period_b_start,
                period_b_to=period_b_end,
            )
        else:
            result = compare_months(
                user_id=user_id,
                period_a_from=prev_month_start,
                period_a_to=prev_month_end,
                period_b_from=this_month_start,
                period_b_to=this_month_end,
            )

        direction = result.get("direction", "no_change")
        pct = result.get("pct_change")
        summary = (
            f"Spending {'increased' if direction == 'increase' else 'decreased' if direction == 'decrease' else 'unchanged'}"
            + (f" by {abs(pct)}%" if pct is not None else "")
            + f": ₹{result['period_a']['total']:,.2f} → ₹{result['period_b']['total']:,.2f}"
        )
        return {"route": ROUTE_ANALYTICS, "intent": intent, "data": result, "summary": summary}

    if intent == "cashflow":
        result = get_cashflow(
            user_id=user_id,
            date_from=parsed.date_from,
            date_to=parsed.date_to,
        )
        summary = f"Income ₹{result['income']:,.2f} · Expense ₹{result['expense']:,.2f} · Net ₹{result['net']:,.2f}"
        return {"route": ROUTE_ANALYTICS, "intent": intent, "data": result, "summary": summary}

    if intent == "subscription_check":
        result = detect_subscriptions(user_id=user_id)
        summary = f"{len(result)} recurring subscription{'' if len(result) == 1 else 's'} detected." if result else "No recurring subscriptions detected."
        return {"route": ROUTE_ANALYTICS, "intent": intent, "data": result, "summary": summary}

    # Fallback
    return {"route": ROUTE_ANALYTICS, "intent": intent, "data": {}}

"""
Hybrid Retrieval Engine powered by Django ORM.

Demonstrates:
  - Complex QuerySet lookups with Q objects (OR logic, icontains)
  - Date range filtering
  - Ordering, slicing, and model serialization
"""

from __future__ import annotations

import logging
from datetime import date
from django.conf import settings
from django.db.models import Q

from .models import Transaction
from .query_parser import ParsedQuery

logger = logging.getLogger(__name__)


def retrieve_transactions_for_query(
    question: str,
    top_k: int | None = None,
    parsed: ParsedQuery | None = None,
    user_id: str | None = None,
) -> list[dict]:
    """
    Main retrieval entry point using Django ORM.

    1. Metadata filter (category / merchant / date / type)
    2. Text search across receiver, description, category, merchant
    3. Broad fallback — return recent transactions
    """
    clean_question = (question or "").strip()
    if not clean_question:
        raise ValueError("question is required")

    limit = top_k or getattr(settings, "RAG_TOP_K", 8)

    qs = Transaction.objects.all()
    if user_id:
        try:
            uid = int(user_id)
            qs = qs.filter(Q(user_id=uid) | Q(user__isnull=True))
        except (ValueError, TypeError):
            qs = qs.filter(user__isnull=True)

    # 1. Metadata filter
    if parsed:
        meta_qs = qs
        has_filter = False

        if parsed.category:
            meta_qs = meta_qs.filter(category_name__icontains=parsed.category)
            has_filter = True
        if parsed.merchant:
            meta_qs = meta_qs.filter(
                Q(normalized_merchant__icontains=parsed.merchant) |
                Q(receiver__icontains=parsed.merchant)
            )
            has_filter = True
        if parsed.transaction_type:
            meta_qs = meta_qs.filter(transaction_type=parsed.transaction_type)
            has_filter = True
        if parsed.date_from:
            meta_qs = meta_qs.filter(date__gte=parsed.date_from)
            has_filter = True
        if parsed.date_to:
            meta_qs = meta_qs.filter(date__lte=parsed.date_to)
            has_filter = True

        if has_filter:
            meta_results = list(meta_qs.order_by("-date")[:limit])
            if meta_results:
                return [t.to_dict() for t in meta_results]

    # 2. Text search across receiver, description, category, normalized_merchant
    text_results = list(
        qs.filter(
            Q(receiver__icontains=clean_question) |
            Q(description__icontains=clean_question) |
            Q(category_name__icontains=clean_question) |
            Q(normalized_merchant__icontains=clean_question)
        ).order_by("-date")[:limit]
    )
    if text_results:
        return [t.to_dict() for t in text_results]

    # 3. Broad fallback
    fallback_results = list(qs.order_by("-date")[:limit])
    return [t.to_dict() for t in fallback_results]

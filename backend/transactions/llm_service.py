import hashlib
import requests
from django.conf import settings
from rest_framework.exceptions import APIException
from .prompts import build_grounded_prompt
from google import genai

# ---------------------------------------------------------------------------
# Simple in-memory response cache
# Caches LLM answers by (question + transaction IDs) so repeated identical
# queries don't make a second network call to Gemini.
# Cache is cleared on server restart — no persistence needed for dev.
# ---------------------------------------------------------------------------
_RESPONSE_CACHE: dict[str, dict] = {}
_CACHE_MAX_SIZE = 200


def _cache_key(question: str, transactions: list[dict]) -> str:
    ids = ",".join(t.get("transaction_id", "") for t in transactions)
    raw = f"{question.strip().lower()}|{ids}"
    return hashlib.md5(raw.encode()).hexdigest()


def _get_cached(key: str) -> dict | None:
    return _RESPONSE_CACHE.get(key)


def _set_cached(key: str, value: dict) -> None:
    if len(_RESPONSE_CACHE) >= _CACHE_MAX_SIZE:
        # Evict oldest entry
        oldest = next(iter(_RESPONSE_CACHE))
        del _RESPONSE_CACHE[oldest]
    _RESPONSE_CACHE[key] = value


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------
def _request_json(url: str, payload: dict, headers: dict, timeout_sec: int) -> dict:
    response = requests.post(url, json=payload, headers=headers, timeout=timeout_sec)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------
def _call_gemini(prompt: str) -> str:
    if not settings.GEMINI_API_KEY:
        raise APIException("GEMINI_API_KEY is missing")

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )
        text = response.text.strip()
        if not text:
            raise APIException("Gemini returned empty text")
        return text
    except Exception as err:
        raise APIException(f"Gemini request failed: {err}") from err


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def answer_question_with_context(question: str, transactions: list[dict]) -> dict:
    if not transactions:
        return {
            "answer": "I do not have enough relevant transaction data to answer this confidently.",
            "provider": "none",
            "provider_errors": [],
        }

    # Check cache first
    cache_key = _cache_key(question, transactions)
    cached = _get_cached(cache_key)
    if cached:
        return {**cached, "cached": True}

    prompt = build_grounded_prompt(question=question, transactions=transactions)

    try:
        answer_text = _call_gemini(prompt)
        result = {
            "answer": answer_text,
            "provider": "gemini",
            "provider_errors": [],
        }
        _set_cached(cache_key, result)
        return result
    except APIException as err:
        raise RuntimeError(f"LLM provider failed: {err}")

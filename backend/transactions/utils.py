from django.conf import settings
from pymongo import MongoClient


_CLIENT = None
_INDEXES_READY = False


def reset_client_cache():
    """Clear the cached Mongo client and index flag when a client exists.
    If no client has been initialized, raise to avoid forcing an unnecessary
    reconnect on the next call.
    """
    global _CLIENT, _INDEXES_READY
    if _CLIENT is None:
        raise RuntimeError("Mongo client is not initialized; nothing to reset.")

    _CLIENT = None
    _INDEXES_READY = False


def _build_tls_kwargs(mongo_uri: str) -> dict:
    """Assemble connection options for MongoClient."""
    kwargs = {
        "serverSelectionTimeoutMS": settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
        "connectTimeoutMS": settings.MONGO_CONNECT_TIMEOUT_MS,
        "socketTimeoutMS": settings.MONGO_SOCKET_TIMEOUT_MS,
    }

    # Extra TLS tweaks only matter for MongoDB Atlas URLs (mongodb+srv://).
    if mongo_uri.startswith("mongodb+srv://"):
        allow_invalid_certs = settings.MONGO_TLS_ALLOW_INVALID_CERTS
        disable_ocsp = settings.MONGO_TLS_DISABLE_OCSP

        # If both toggles are on, prefer OCSP checks over allowing invalid certs.
        if allow_invalid_certs and disable_ocsp:
            disable_ocsp = False

        if allow_invalid_certs:
            kwargs["tlsAllowInvalidCertificates"] = True
        elif disable_ocsp:
            kwargs["tlsDisableOCSPEndpointCheck"] = True

        # Try to supply a CA bundle so TLS works even when the system store is missing roots.
        try:
            import certifi

            kwargs["tls"] = True
            kwargs["tlsCAFile"] = certifi.where()
        except Exception:
            pass

    return kwargs


def _build_client():
    primary_uri = (settings.MONGO_URI or "").strip()
    if not primary_uri:
        raise RuntimeError("MONGO_URI is missing. Add it in backend/.env.")

    fallback_uri = (getattr(settings, "MONGO_URI_FALLBACK", "") or "").strip()
    uris_to_try = [primary_uri] + ([fallback_uri] if fallback_uri else [])
    last_error = None

    for mongo_uri in uris_to_try:
        kwargs = _build_tls_kwargs(mongo_uri)
        try:
            client = MongoClient(mongo_uri, **kwargs)
            client.admin.command("ping")
            return client
        except Exception as primary_error:
            last_error = primary_error
            if not mongo_uri.startswith("mongodb+srv://"):
                continue

            # Atlas TLS fallback for local dev environments that fail strict handshake checks.
            relaxed_kwargs = dict(kwargs)
            relaxed_kwargs["tls"] = True
            relaxed_kwargs["tlsAllowInvalidCertificates"] = True
            relaxed_kwargs.pop("tlsDisableOCSPEndpointCheck", None)
            relaxed_kwargs.pop("tlsCAFile", None)

            try:
                relaxed_client = MongoClient(mongo_uri, **relaxed_kwargs)
                relaxed_client.admin.command("ping")
                return relaxed_client
            except Exception as relaxed_error:
                last_error = relaxed_error
                continue

    raise RuntimeError("Database connection failed; please verify MongoDB is reachable.") from last_error


def get_db():
    global _CLIENT, _INDEXES_READY
    if _CLIENT is None:
        _CLIENT = _build_client()

    if not settings.DB_NAME:
        raise RuntimeError("DB_NAME is missing. Add it in backend/.env.")

    db = _CLIENT[settings.DB_NAME]
    collection_name = settings.MONGO_TRANSACTIONS_COLLECTION
    collection = db[collection_name]

    if not _INDEXES_READY:
        collection.create_index(
            [("transaction_id", 1)],
            name="transaction_id_unique_non_null",
            unique=True,
            partialFilterExpression={"transaction_id": {"$type": "string"}},
        )
        collection.create_index("date")
        collection.create_index("receiver")
        collection.create_index("category")
        # New indexes for analytics + user-scoped retrieval
        collection.create_index("user_id")
        collection.create_index("normalized_merchant")
        collection.create_index("transaction_type")
        collection.create_index([("user_id", 1), ("date", -1)])
        collection.create_index([("user_id", 1), ("category", 1)])
        collection.create_index([("user_id", 1), ("normalized_merchant", 1)])
        _INDEXES_READY = True

    return db

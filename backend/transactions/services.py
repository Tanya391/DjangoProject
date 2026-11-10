"""
Transaction ingestion and data generation service.

Supports both Django ORM (Relational SQLite/PostgreSQL) as primary storage
with graceful synchronization to MongoDB if configured.
"""

import csv
import hashlib
import random
import uuid
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from typing import Literal

from django.conf import settings
from django.contrib.auth import get_user_model
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from .models import Transaction, Category
from .categorizer import categorize_transaction
from .merchant_normalizer import normalize_merchant

User = get_user_model()


class TransactionRowSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    date: date
    receiver: str = Field(min_length=1)
    description: str = Field(min_length=1)
    amount: float
    transaction_type: Literal["debit", "credit"]
    balance: float = 0.0
    transaction_id: str | None = None

    @field_validator("date", mode="before")
    @classmethod
    def validate_date_present(cls, value):
        if value is None:
            raise ValueError("date is required")
        if isinstance(value, str) and not value.strip():
            raise ValueError("date is required")
        return value

    @field_validator("transaction_type", mode="before")
    @classmethod
    def normalize_transaction_type(cls, value):
        if value is None:
            raise ValueError("transaction_type is required")
        return str(value).strip().lower()


def generate_transaction_id(row: TransactionRowSchema) -> str:
    unique_string = "|".join(
        [
            row.date.isoformat(),
            row.receiver.lower(),
            row.description.lower(),
            f"{row.amount:.2f}",
            row.transaction_type,
        ]
    )
    return hashlib.sha256(unique_string.encode("utf-8")).hexdigest()


def _resolve_transaction_id(row: TransactionRowSchema) -> str:
    if row.transaction_id and row.transaction_id.strip():
        return row.transaction_id.strip()
    return generate_transaction_id(row)


def _sync_to_mongo_if_available(tx_dicts: list[dict]):
    """Optional sync to Mongo if MongoDB is explicitly enabled in settings."""
    if not getattr(settings, "ENABLE_MONGO_SYNC", False):
        return
    try:
        from .utils import get_db
        db = get_db()
        col = db[settings.MONGO_TRANSACTIONS_COLLECTION]
        for tx in tx_dicts:
            col.update_one(
                {"transaction_id": tx["transaction_id"]},
                {"$set": tx},
                upsert=True
            )
    except Exception:
        pass


def ingest_csv(file_path: str, return_report: bool = False, user_id: str | None = None):
    """
    Ingest a CSV file of transactions into Django ORM database.

    Args:
        file_path: Path to the CSV file.
        return_report: If True, return a detailed ingestion report dict.
        user_id: Optional user ID to associate transactions with a specific user.
    """
    report = {
        "inserted_count": 0,
        "duplicate_count": 0,
        "invalid_count": 0,
        "invalid_rows": [],
    }

    user = None
    if user_id:
        try:
            user = User.objects.get(id=int(user_id))
        except (User.DoesNotExist, ValueError):
            user = None

    mongo_sync_list = []

    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row_number, raw_row in enumerate(reader, start=2):
            try:
                row = TransactionRowSchema.model_validate(raw_row)
            except ValidationError as exc:
                report["invalid_count"] += 1
                report["invalid_rows"].append(
                    {
                        "row_number": row_number,
                        "error": exc.errors()[0]["msg"],
                    }
                )
                continue

            tx_id = _resolve_transaction_id(row)
            normalized = normalize_merchant(row.receiver)
            cat_name = categorize_transaction(row.receiver, row.description, row.transaction_type)
            cat_obj, _ = Category.objects.get_or_create(name=cat_name.lower())

            # Django ORM insert / get_or_create
            tx_obj, created = Transaction.objects.get_or_create(
                transaction_id=tx_id,
                defaults={
                    "user": user,
                    "date": row.date,
                    "receiver": row.receiver,
                    "normalized_merchant": normalized,
                    "category": cat_obj,
                    "category_name": cat_name,
                    "description": row.description,
                    "amount": Decimal(str(row.amount)),
                    "transaction_type": row.transaction_type,
                    "balance": Decimal(str(row.balance)),
                }
            )

            if created:
                report["inserted_count"] += 1
                mongo_sync_list.append(tx_obj.to_dict())
            else:
                report["duplicate_count"] += 1

    if mongo_sync_list:
        _sync_to_mongo_if_available(mongo_sync_list)

    if return_report:
        return report
    return report["inserted_count"]


def _create_orm_transaction(user, date_obj, amount, tx_type, desc, merchant, cat_name):
    cat_obj, _ = Category.objects.get_or_create(name=cat_name.lower())
    tx_id = str(uuid.uuid4())
    return Transaction(
        transaction_id=tx_id,
        user=user,
        date=date_obj.date() if isinstance(date_obj, datetime) else date_obj,
        amount=Decimal(str(round(amount, 2))),
        transaction_type=tx_type,
        description=desc,
        receiver=merchant,
        normalized_merchant=merchant,
        category=cat_obj,
        category_name=cat_name,
    )


def generate_demo_data(user_id: str | int, months: int = 6) -> int:
    """
    Generates realistic transaction data for a user and saves to Django ORM.
    Returns count of created transactions.
    """
    try:
        user = User.objects.get(id=int(user_id)) if user_id else None
    except (User.DoesNotExist, ValueError):
        user = None

    end_date = datetime.now()
    start_date = end_date - relativedelta(months=months)

    transactions_to_create = []

    merchants = {
        "groceries": ["DMart", "BigBasket", "Reliance Fresh", "Nature's Basket"],
        "food_delivery": ["Zomato", "Swiggy", "Starbucks", "Dominos", "Local Cafe"],
        "shopping": ["Amazon", "Flipkart", "Myntra", "Zara", "H&M"],
        "utilities": ["Electricity Board", "Jio", "Airtel", "Water Bill"],
        "entertainment": ["Netflix", "Spotify", "PVR Cinemas", "BookMyShow"],
        "travel": ["Uber", "Ola", "Indian Railways", "Metro"],
        "medical": ["Apollo Pharmacy", "Practo", "Local Clinic"],
    }

    current_date = start_date
    while current_date <= end_date:
        # Salary credit on 1st of month
        salary_date = datetime(current_date.year, current_date.month, 1)
        if start_date <= salary_date <= end_date:
            transactions_to_create.append(
                _create_orm_transaction(
                    user, salary_date, 85000.0, "credit", "Monthly Salary", "TechCorp Inc.", "salary"
                )
            )

        # Rent debit on 5th
        rent_date = datetime(current_date.year, current_date.month, 5)
        if start_date <= rent_date <= end_date:
            transactions_to_create.append(
                _create_orm_transaction(
                    user, rent_date, 22000.0, "debit", "Monthly Rent", "Landlord", "rent"
                )
            )

        num_tx = random.randint(20, 35)
        for _ in range(num_tx):
            random_day = random.randint(1, 28)
            tx_date = datetime(current_date.year, current_date.month, random_day)
            if not (start_date <= tx_date <= end_date):
                continue

            cat = random.choice(list(merchants.keys()))
            merchant = random.choice(merchants[cat])

            if cat == "groceries":
                amt = random.uniform(500, 3000)
            elif cat == "food_delivery":
                amt = random.uniform(200, 1500)
            elif cat == "shopping":
                amt = random.uniform(1000, 5000)
            elif cat == "utilities":
                amt = random.uniform(800, 2500)
            elif cat == "entertainment":
                amt = random.uniform(199, 999)
            elif cat == "travel":
                amt = random.uniform(100, 800)
            else:
                amt = random.uniform(200, 2000)

            transactions_to_create.append(
                _create_orm_transaction(
                    user, tx_date, round(amt, 2), "debit", f"{cat} Payment", merchant, cat
                )
            )

        current_date += relativedelta(months=1)
        current_date = datetime(current_date.year, current_date.month, 1)

    if transactions_to_create:
        Transaction.objects.bulk_create(transactions_to_create, ignore_conflicts=True)
        # Optional background sync to Mongo
        _sync_to_mongo_if_available([t.to_dict() for t in transactions_to_create])

    return len(transactions_to_create)

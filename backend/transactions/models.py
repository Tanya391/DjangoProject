import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Category(models.Model):
    """
    Relational Category model to demonstrate Foreign Key relationships
    and ORM queries as required by Django course syllabus.
    """
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True, default="")
    icon = models.CharField(max_length=50, blank=True, default="tag")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """
    Primary financial transaction record stored via Django ORM.
    Demonstrates:
      - Field types (CharField, DecimalField, DateField, BooleanField, ForeignKey)
      - Foreign Keys with CASCADE / SET_NULL behaviors
      - Model methods, __str__, and Meta ordering
      - ORM QuerySet integration
    """
    TRANSACTION_TYPE_CHOICES = [
        ("debit", "Debit / Expense"),
        ("credit", "Credit / Income"),
    ]

    transaction_id = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        default=uuid.uuid4,
        help_text="Unique SHA-256 or UUID hash for transaction deduplication."
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True,
        help_text="User who owns this transaction record."
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
        help_text="Categorization entity linked via Foreign Key."
    )
    category_name = models.CharField(max_length=100, db_index=True, default="other")
    date = models.DateField(db_index=True, default=timezone.now)
    receiver = models.CharField(max_length=255, help_text="Merchant or payee name")
    normalized_merchant = models.CharField(max_length=255, db_index=True, blank=True, default="")
    description = models.TextField(blank=True, default="")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES,
        default="debit"
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_subscription = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["category_name", "date"]),
        ]

    def __str__(self):
        return f"{self.date} | {self.receiver} | {self.transaction_type.upper()} ₹{self.amount}"

    def save(self, *args, **kwargs):
        # Auto-normalize merchant name if not provided
        if not self.normalized_merchant:
            from .merchant_normalizer import normalize_merchant
            self.normalized_merchant = normalize_merchant(self.receiver)

        # Sync category_name with Category foreign key if linked
        if self.category and not self.category_name:
            self.category_name = self.category.name
        elif not self.category and self.category_name:
            # Try to associate with Category object
            cat_obj, _ = Category.objects.get_or_create(name=self.category_name.lower())
            self.category = cat_obj

        super().save(*args, **kwargs)

    def to_dict(self):
        """Converts model instance to JSON-serializable dict matching API format."""
        return {
            "transaction_id": self.transaction_id,
            "user_id": str(self.user.id) if self.user else None,
            "date": self.date.isoformat() if hasattr(self.date, "isoformat") else str(self.date),
            "receiver": self.receiver,
            "normalized_merchant": self.normalized_merchant,
            "description": self.description,
            "amount": float(self.amount),
            "transaction_type": self.transaction_type,
            "category": self.category_name,
            "balance": float(self.balance),
            "is_subscription": self.is_subscription,
        }

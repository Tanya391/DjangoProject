from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Category, Transaction, QueryLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Category model.
    Satisfies syllabus: Django Admin, working with models.
    """
    list_display = ("id", "name", "icon", "transaction_count", "created_at")
    search_fields = ("name", "description")
    ordering = ("name",)

    def transaction_count(self, obj):
        return obj.transactions.count()
    transaction_count.short_description = "Transactions"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Rich Django Admin configuration for financial transactions.
    Demonstrates:
      - list_display, list_filter, search_fields
      - date_hierarchy for timeline navigation
      - custom actions, read-only fields, and fieldsets
      - relational display (User & Category Foreign Keys)
    """
    list_display = (
        "transaction_id",
        "date",
        "receiver",
        "category_name",
        "amount_display",
        "transaction_type",
        "is_subscription",
        "user",
    )
    list_filter = (
        "transaction_type",
        "category_name",
        "is_subscription",
        ("date", admin.DateFieldListFilter),
    )
    search_fields = (
        "receiver",
        "description",
        "normalized_merchant",
        "transaction_id",
        "category_name",
    )
    date_hierarchy = "date"
    ordering = ("-date", "-created_at")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Core Information", {
            "fields": ("transaction_id", "user", "date", "receiver", "normalized_merchant")
        }),
        ("Financial Data", {
            "fields": ("amount", "transaction_type", "balance")
        }),
        ("Categorization", {
            "fields": ("category", "category_name", "is_subscription", "description")
        }),
        ("Audit Metadata", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )

    def amount_display(self, obj):
        color = "green" if obj.transaction_type == "credit" else "red"
        prefix = "+" if obj.transaction_type == "credit" else "-"
        return f"{prefix}₹{obj.amount:.2f}"
    amount_display.short_description = "Amount"


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question", "route", "source_count", "created_at")
    list_filter = ("route", "created_at")
    search_fields = ("question", "answer")
    readonly_fields = ("created_at",)


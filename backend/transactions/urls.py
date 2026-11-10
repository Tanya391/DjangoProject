from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AskQuestionView,
    StatusView,
    LoginView,
    LogoutView,
    RegisterView,
    RetrieveTransactionsView,
    MonthlySummaryView,
    CategoryBreakdownView,
    TopMerchantsView,
    CashflowView,
    SubscriptionsView,
    SeedDemoDataView,
    UploadTransactionsView,
    TransactionListView,
    QueryHistoryView,
)

urlpatterns = [
    # Health check
    path("status/", StatusView.as_view(), name="status"),

    # Authentication (JWT + Django User Auth)
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),

    # Core AI & Natural Language Query endpoints
    path("retrieve/", RetrieveTransactionsView.as_view(), name="retrieve-transactions"),
    path("ask/", AskQuestionView.as_view(), name="ask-question"),
    path("history/", QueryHistoryView.as_view(), name="query-history"),

    # Analytics endpoints (powered by Django ORM aggregations)
    path("monthly-summary/", MonthlySummaryView.as_view(), name="monthly-summary"),
    path("spending-by-category/", CategoryBreakdownView.as_view(), name="spending-by-category"),
    path("top-merchants/", TopMerchantsView.as_view(), name="top-merchants"),
    path("cashflow/", CashflowView.as_view(), name="cashflow"),
    path("subscriptions/", SubscriptionsView.as_view(), name="subscriptions"),

    # Data ingestion & transactions
    path("seed/", SeedDemoDataView.as_view(), name="seed-demo-data"),
    path("upload/", UploadTransactionsView.as_view(), name="upload-transactions"),
    path("transactions/", TransactionListView.as_view(), name="list-transactions"),
]

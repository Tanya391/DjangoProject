"""
URL configuration for FinAgent backend.

Routes:
  - Django Admin panel (/admin/)
  - REST Framework APIs (/api/v1/) consumed by React frontend
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("transactions.urls")),
]

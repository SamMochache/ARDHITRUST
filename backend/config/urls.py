# config/urls.py — FULL REPLACEMENT
# FIX 8: Health check and metrics endpoints added

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerUIView
from core.health import DetailedHealthView, HealthView, MetricsView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # FIX 8: Health checks — must be BEFORE auth middleware hits
    path("api/health/",          HealthView.as_view(),         name="health"),
    path("api/health/detailed/", DetailedHealthView.as_view(), name="health-detailed"),
    path("api/metrics/",         MetricsView.as_view(),        name="metrics"),

    # API docs
    path("api/schema/", SpectacularAPIView.as_view(),                         name="schema"),
    path("api/docs/",   SpectacularSwaggerUIView.as_view(url_name="schema"),  name="swagger-ui"),

    # Application routes
    path("api/v1/auth/",           include("apps.accounts.urls")),
    path("api/v1/properties/",     include("apps.properties.urls")),
    path("api/v1/verification/",   include("apps.verification.urls")),
    path("api/v1/escrow/",         include("apps.escrow.urls")),
    path("api/v1/messaging/",      include("apps.messaging.urls")),
    path("api/v1/services/",       include("apps.services.urls")),
    path("api/v1/agents/",         include("apps.agents.urls")),
]
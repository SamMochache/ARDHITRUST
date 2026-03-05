# config/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerUIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/",   SpectacularSwaggerUIView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/properties/", include("apps.properties.urls")),
    path("api/v1/auth/",       include("apps.accounts.urls")),
    path("api/v1/verification/", include("apps.verification.urls")),
    path("api/v1/escrow/",     include("apps.escrow.urls")),
    path("api/v1/messaging/",  include("apps.messaging.urls")),
    path("api/v1/services/",   include("apps.services.urls")),
    path("api/v1/agents/",     include("apps.agents.urls")),
]

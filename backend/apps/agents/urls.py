# apps/agents/urls.py
from django.urls import path
from .views import BuyerAssistantView, ValuationView

urlpatterns = [
    path("assistant/",  BuyerAssistantView.as_view(), name="agent-assistant"),
    path("valuation/",  ValuationView.as_view(),      name="agent-valuation"),
]
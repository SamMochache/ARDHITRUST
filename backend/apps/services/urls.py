# apps/services/urls.py
from django.urls import path
from .views import QuoteSubmitView, ServiceRequestCreateView

urlpatterns = [
    path("request/", ServiceRequestCreateView.as_view(), name="service-request"),
    path("quotes/",  QuoteSubmitView.as_view(),           name="quote-submit"),
]
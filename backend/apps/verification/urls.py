# apps/verification/urls.py
from django.urls import path
from .views import VerificationRequestView, VerificationStatusView

urlpatterns = [
    path("<uuid:property_id>/status/", VerificationStatusView.as_view(), name="verification-status"),
    path("request/",                   VerificationRequestView.as_view(), name="verification-request"),
]
# apps/escrow/urls.py
from django.urls import path
from .views import EscrowAdvanceView, EscrowInitiateView, EscrowStatusView, MpesaCallbackView

urlpatterns = [
    path("initiate/",            EscrowInitiateView.as_view(),  name="escrow-initiate"),
    path("<uuid:pk>/status/",    EscrowStatusView.as_view(),    name="escrow-status"),
    path("<uuid:pk>/advance/",   EscrowAdvanceView.as_view(),   name="escrow-advance"),
    path("mpesa/callback/",      MpesaCallbackView.as_view(),   name="mpesa-callback"),
]
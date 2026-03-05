# apps/accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import KYCStatusView, KYCSubmitView, MeView, RegisterView

urlpatterns = [
    path("register/",     RegisterView.as_view(),      name="auth-register"),
    path("token/",        TokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(),  name="token-refresh"),
    path("me/",           MeView.as_view(),             name="auth-me"),
    path("kyc/submit/",   KYCSubmitView.as_view(),      name="kyc-submit"),
    path("kyc/status/",   KYCStatusView.as_view(),      name="kyc-status"),
]
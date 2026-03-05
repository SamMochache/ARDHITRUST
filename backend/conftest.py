# conftest.py  — must live at the backend/ root (same directory as manage.py)
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def buyer(db):
    from apps.accounts.models import KYCProfile
    user = User.objects.create_user(
        email="buyer@test.com",
        phone="0712345678",
        first_name="Jane",
        last_name="Buyer",
        role="BUYER",
        password="testpass123",
    )
    KYCProfile.objects.get_or_create(user=user)
    return user


@pytest.fixture
def seller(db):
    from apps.accounts.models import KYCProfile
    user = User.objects.create_user(
        email="seller@test.com",
        phone="0712345679",
        first_name="John",
        last_name="Seller",
        role="SELLER",
        password="testpass123",
    )
    KYCProfile.objects.create(
        user=user, status="APPROVED",
        iprs_verified=True, kra_verified=True,
    )
    return user


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(
        email="admin@test.com",
        phone="0712345680",
        first_name="Admin",
        last_name="User",
        role="ADMIN",
        password="testpass123",
        is_staff=True,
        is_superuser=True,
    )
    return user


@pytest.fixture
def property_obj(db, seller):
    from apps.properties.models import Property
    return Property.objects.create(
        seller=seller,
        title="Test Plot Nairobi",
        description="A beautiful test plot in Westlands",
        county="Nairobi",
        area_name="Westlands",
        lr_number="LR/123/456",
        lr_number_encrypted="LR/123/456",
        property_type="RESIDENTIAL",
        size_acres="0.5",
        price_kes=5_000_000,
        status="ACTIVE",
        trust_score=75,
    )


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def buyer_client(api_client, buyer):
    from rest_framework_simplejwt.tokens import RefreshToken
    token = RefreshToken.for_user(buyer)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
    return api_client


@pytest.fixture
def seller_client(api_client, seller):
    from rest_framework_simplejwt.tokens import RefreshToken
    token = RefreshToken.for_user(seller)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    from rest_framework_simplejwt.tokens import RefreshToken
    token = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
    return api_client
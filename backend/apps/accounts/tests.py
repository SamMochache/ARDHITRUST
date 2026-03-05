# apps/accounts/tests.py
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

REGISTER_URL = "/api/v1/auth/register/"


@pytest.mark.django_db
class TestRegister:
    def test_buyer_success(self, api_client):
        r = api_client.post(REGISTER_URL, {
            "email": "new@test.com", "phone": "0700000001",
            "first_name": "New", "last_name": "User",
            "role": "BUYER", "password": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        assert r.status_code == 201
        assert r.data["email"] == "new@test.com"
        assert r.data["kyc_status"] == "PENDING"
        assert "password" not in r.data

    def test_seller_success(self, api_client):
        r = api_client.post(REGISTER_URL, {
            "email": "s@test.com", "phone": "0700000002",
            "first_name": "S", "last_name": "U",
            "role": "SELLER", "password": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        assert r.status_code == 201
        assert r.data["role"] == "SELLER"

    def test_password_mismatch(self, api_client):
        r = api_client.post(REGISTER_URL, {
            "email": "x@test.com", "phone": "0700000003",
            "first_name": "X", "last_name": "Y",
            "role": "BUYER", "password": "StrongPass123!",
            "password2": "Wrong!",
        })
        assert r.status_code == 400

    def test_duplicate_email(self, api_client, buyer):
        r = api_client.post(REGISTER_URL, {
            "email": buyer.email, "phone": "0700000099",
            "first_name": "D", "last_name": "U",
            "role": "BUYER", "password": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        assert r.status_code == 400

    def test_duplicate_phone(self, api_client, buyer):
        r = api_client.post(REGISTER_URL, {
            "email": "unique@test.com", "phone": buyer.phone,
            "first_name": "D", "last_name": "U",
            "role": "BUYER", "password": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        assert r.status_code == 400

    def test_admin_role_blocked(self, api_client):
        """Cannot self-register as ADMIN."""
        r = api_client.post(REGISTER_URL, {
            "email": "h@test.com", "phone": "0700000010",
            "first_name": "H", "last_name": "X",
            "role": "ADMIN", "password": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        assert r.status_code == 400


@pytest.mark.django_db
class TestTokenAuth:
    def test_obtain_token(self, api_client, buyer):
        r = api_client.post("/api/v1/auth/token/", {
            "email": buyer.email, "password": "testpass123",
        })
        assert r.status_code == 200
        assert "access" in r.data and "refresh" in r.data

    def test_wrong_password(self, api_client, buyer):
        r = api_client.post("/api/v1/auth/token/", {
            "email": buyer.email, "password": "wrongpassword",
        })
        assert r.status_code == 401

    def test_token_refresh(self, api_client, buyer):
        t = api_client.post("/api/v1/auth/token/", {
            "email": buyer.email, "password": "testpass123",
        })
        r = api_client.post("/api/v1/auth/token/refresh/", {"refresh": t.data["refresh"]})
        assert r.status_code == 200
        assert "access" in r.data


@pytest.mark.django_db
class TestMeView:
    def test_authenticated(self, buyer_client, buyer):
        r = buyer_client.get("/api/v1/auth/me/")
        assert r.status_code == 200
        assert r.data["email"] == buyer.email
        assert r.data["role"] == "BUYER"

    def test_unauthenticated(self, api_client):
        r = api_client.get("/api/v1/auth/me/")
        assert r.status_code == 401


@pytest.mark.django_db
class TestKYCSubmit:
    URL = "/api/v1/auth/kyc/submit/"

    def test_success(self, buyer_client):
        r = buyer_client.post(self.URL, {
            "national_id": "12345678",
            "kra_pin": "A123456789Z",
            "id_front_key": "docs/front.jpg",
            "id_back_key": "docs/back.jpg",
        })
        assert r.status_code == 200
        assert "submitted" in r.data["detail"].lower()

    def test_invalid_national_id_letters(self, buyer_client):
        r = buyer_client.post(self.URL, {
            "national_id": "ABCDEFGH",
            "kra_pin": "A123456789Z",
            "id_front_key": "k", "id_back_key": "k",
        })
        assert r.status_code == 400

    def test_national_id_too_short(self, buyer_client):
        r = buyer_client.post(self.URL, {
            "national_id": "123456",
            "kra_pin": "A123456789Z",
            "id_front_key": "k", "id_back_key": "k",
        })
        assert r.status_code == 400

    def test_invalid_kra_pin(self, buyer_client):
        r = buyer_client.post(self.URL, {
            "national_id": "12345678",
            "kra_pin": "NOTAPIN",
            "id_front_key": "k", "id_back_key": "k",
        })
        assert r.status_code == 400

    def test_unauthenticated_rejected(self, api_client):
        r = api_client.post(self.URL, {})
        assert r.status_code == 401

    def test_already_approved_rejected(self, seller_client):
        r = seller_client.post(self.URL, {
            "national_id": "12345678", "kra_pin": "A123456789Z",
            "id_front_key": "k", "id_back_key": "k",
        })
        assert r.status_code == 400


@pytest.mark.django_db
class TestKYCStatus:
    def test_status_view(self, buyer_client):
        r = buyer_client.get("/api/v1/auth/kyc/status/")
        assert r.status_code == 200
        assert "status" in r.data


@pytest.mark.django_db
class TestCustomUserManager:
    def test_normalises_email(self, db):
        u = User.objects.create_user(
            email="TEST@Example.COM", phone="0799999999",
            first_name="T", last_name="U", password="pass123",
        )
        assert u.email == "TEST@example.com"

    def test_requires_email(self, db):
        with pytest.raises(ValueError, match="Email"):
            User.objects.create_user(email="", phone="0799999998", password="x")

    def test_requires_phone(self, db):
        with pytest.raises(ValueError, match="Phone"):
            User.objects.create_user(email="a@b.com", phone="", password="x")

    def test_create_superuser(self, db):
        su = User.objects.create_superuser(
            email="su@test.com", phone="0799999997", password="superpass123",
        )
        assert su.is_staff and su.is_superuser and su.role == "ADMIN"

    def test_get_full_name(self, buyer):
        assert buyer.get_full_name() == "Jane Buyer"
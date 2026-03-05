# apps/services/tests.py
import pytest
from apps.services.models import ServiceRequest


def _approved_client(db, role="VALUER"):
    from django.contrib.auth import get_user_model
    from apps.accounts.models import KYCProfile
    from rest_framework_simplejwt.tokens import RefreshToken
    from rest_framework.test import APIClient
    User = get_user_model()
    user = User.objects.create_user(
        email=f"{role.lower()}@test.com", phone="0700000055",
        first_name="V", last_name="R", role=role, password="x",
    )
    KYCProfile.objects.create(user=user, status="APPROVED")
    c = APIClient()
    token = RefreshToken.for_user(user)
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
    return c, user


@pytest.mark.django_db
class TestServiceRequest:
    URL = "/api/v1/services/request/"

    def test_approved_buyer_can_request(self, db, property_obj):
        c, _ = _approved_client(db, role="BUYER")
        # Need KYC approved for buyer
        from django.contrib.auth import get_user_model
        from apps.accounts.models import KYCProfile
        User = get_user_model()
        u = User.objects.get(email="buyer@test.com")
        u.kyc.status = KYCProfile.Status.APPROVED
        u.kyc.save()
        r = c.post(self.URL, {
            "property_id": str(property_obj.id),
            "service_type": "VALUATION",
        })
        assert r.status_code == 201
        assert r.data["service_type"] == "VALUATION"

    def test_unapproved_user_blocked(self, buyer_client, property_obj):
        r = buyer_client.post(self.URL, {
            "property_id": str(property_obj.id),
            "service_type": "VALUATION",
        })
        assert r.status_code == 403

    def test_invalid_service_type(self, seller_client, property_obj):
        # seller has approved KYC so passes auth
        r = seller_client.post(self.URL, {
            "property_id": str(property_obj.id),
            "service_type": "MAGIC",
        })
        assert r.status_code == 400


@pytest.mark.django_db
class TestQuoteSubmit:
    URL = "/api/v1/services/quotes/"

    def test_valuer_can_quote(self, db, property_obj, seller):
        c, valuer = _approved_client(db, role="VALUER")
        req = ServiceRequest.objects.create(
            property=property_obj, requester=seller,
            service_type="VALUATION", status="OPEN",
        )
        r = c.post(self.URL, {
            "request_id": str(req.id),
            "amount_kes": 25000,
            "details": "Full valuation report",
            "estimated_days": 3,
        })
        assert r.status_code == 201
        assert r.data["amount_kes"] == 25000

    def test_surveyor_can_quote(self, db, property_obj, seller):
        c, _ = _approved_client(db, role="SURVEYOR")
        req = ServiceRequest.objects.create(
            property=property_obj, requester=seller,
            service_type="SURVEY", status="OPEN",
        )
        r = c.post(self.URL, {
            "request_id": str(req.id),
            "amount_kes": 30000,
            "details": "Boundary survey",
            "estimated_days": 5,
        })
        assert r.status_code == 201

    def test_buyer_cannot_quote(self, buyer_client, property_obj, seller):
        req = ServiceRequest.objects.create(
            property=property_obj, requester=seller,
            service_type="VALUATION", status="OPEN",
        )
        r = buyer_client.post(self.URL, {
            "request_id": str(req.id),
            "amount_kes": 25000,
            "details": "x",
            "estimated_days": 3,
        })
        assert r.status_code == 403
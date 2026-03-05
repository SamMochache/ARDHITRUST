# apps/verification/tests.py
import pytest
from apps.verification.services.ardhisasa_client import ArdhisasaClient
from apps.verification.services.trust_score import calculate_trust_score


@pytest.mark.django_db
class TestArdhisasaMock:
    def test_mock_confirmed(self):
        r = ArdhisasaClient().land_search("LR/123/456")
        assert r.ownership_confirmed is True
        assert r.registered_owner == "JOHN DOE MWANGI"

    def test_mock_no_encumbrances(self):
        r = ArdhisasaClient().land_search("LR/999/999")
        assert r.encumbrances == []

    def test_mock_rates_cleared(self):
        r = ArdhisasaClient().land_search("ANY/LR")
        assert r.rates_cleared is True

    def test_mock_no_caveat(self):
        r = ArdhisasaClient().land_search("ANY/LR")
        assert r.caveat_present is False


@pytest.mark.django_db
class TestTrustScore:
    def _ver(self, property_obj, **overrides):
        from apps.verification.models import VerificationRequest, VerificationResult
        defaults = dict(
            ownership_confirmed=True, registered_owner="Owner",
            encumbrances_json=[], caveat_present=False, rates_cleared=True,
        )
        defaults.update(overrides)
        req = VerificationRequest.objects.create(
            property=property_obj, requested_by=property_obj.seller,
        )
        return VerificationResult.objects.create(request=req, **defaults)

    def test_perfect_score(self, property_obj):
        assert calculate_trust_score(self._ver(property_obj), property_obj) == 100

    def test_encumbrance_minus_20(self, property_obj):
        ver = self._ver(property_obj, encumbrances_json=[{"type": "mortgage"}])
        assert calculate_trust_score(ver, property_obj) == 80

    def test_caveat_minus_25(self, property_obj):
        ver = self._ver(property_obj, caveat_present=True)
        assert calculate_trust_score(ver, property_obj) == 75

    def test_unconfirmed_minus_30(self, property_obj):
        ver = self._ver(property_obj, ownership_confirmed=False)
        assert calculate_trust_score(ver, property_obj) == 70

    def test_rates_not_cleared_minus_15(self, property_obj):
        ver = self._ver(property_obj, rates_cleared=False)
        assert calculate_trust_score(ver, property_obj) == 85

    def test_worst_case_is_10(self, property_obj):
        ver = self._ver(
            property_obj, ownership_confirmed=False,
            encumbrances_json=[{"type": "mortgage"}],
            caveat_present=True, rates_cleared=False,
        )
        assert calculate_trust_score(ver, property_obj) == 10


@pytest.mark.django_db
class TestVerificationViews:
    def test_status_not_started(self, buyer_client, property_obj):
        r = buyer_client.get(f"/api/v1/verification/{property_obj.id}/status/")
        assert r.status_code == 200
        assert r.data["status"] == "NOT_STARTED"

    def test_status_after_verification(self, buyer_client, property_obj):
        from apps.verification.models import VerificationRequest, VerificationResult
        req = VerificationRequest.objects.create(
            property=property_obj, requested_by=property_obj.seller, status="COMPLETED",
        )
        VerificationResult.objects.create(
            request=req, ownership_confirmed=True, registered_owner="Test",
            encumbrances_json=[], caveat_present=False, rates_cleared=True,
        )
        r = buyer_client.get(f"/api/v1/verification/{property_obj.id}/status/")
        assert r.status_code == 200
        assert r.data["result"]["ownership_confirmed"] is True

    def test_unauthenticated_blocked(self, api_client, property_obj):
        r = api_client.get(f"/api/v1/verification/{property_obj.id}/status/")
        assert r.status_code == 401

    def test_unknown_property_404(self, buyer_client):
        r = buyer_client.get("/api/v1/verification/00000000-0000-0000-0000-000000000000/status/")
        assert r.status_code == 404
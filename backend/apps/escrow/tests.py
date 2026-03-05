# apps/escrow/tests.py
import pytest
from unittest.mock import patch
from apps.escrow.models import EscrowTransaction
from apps.escrow.state_machine import EscrowStateMachine


def _txn(property_obj, buyer, seller, status="INITIATED"):
    return EscrowTransaction.objects.create(
        property=property_obj, buyer=buyer, seller=seller,
        amount_kes=5_000_000, platform_fee_kes=75_000, status=status,
    )


@pytest.mark.django_db
class TestStateMachine:
    def test_fund(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller)
        EscrowStateMachine(t).fund()
        assert t.status == "FUNDED"

    def test_full_happy_path(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller)
        m = EscrowStateMachine(t)
        m.fund(); m.start_search(); m.sign_agreement()
        m.board_approval(); m.transfer_title(); m.complete()
        assert t.status == "COMPLETED"

    def test_dispute_from_funded(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller, status="FUNDED")
        EscrowStateMachine(t).dispute()
        assert t.status == "DISPUTED"

    def test_refund_from_disputed(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller, status="DISPUTED")
        EscrowStateMachine(t).refund()
        assert t.status == "REFUNDED"

    def test_invalid_transition_raises(self, property_obj, buyer, seller):
        from transitions import MachineError
        t = _txn(property_obj, buyer, seller, status="COMPLETED")
        with pytest.raises(MachineError):
            EscrowStateMachine(t).fund()

    def test_dispute_not_allowed_from_completed(self, property_obj, buyer, seller):
        from transitions import MachineError
        t = _txn(property_obj, buyer, seller, status="COMPLETED")
        with pytest.raises(MachineError):
            EscrowStateMachine(t).dispute()


@pytest.mark.django_db
class TestEscrowInitiateView:
    def test_buyer_without_kyc_blocked(self, buyer_client, property_obj):
        r = buyer_client.post("/api/v1/escrow/initiate/",
                              {"property_id": str(property_obj.id)})
        assert r.status_code == 403

    def test_seller_cannot_buy_own(self, seller_client, property_obj):
        r = seller_client.post("/api/v1/escrow/initiate/",
                               {"property_id": str(property_obj.id)})
        assert r.status_code == 400

    def test_approved_buyer_initiates(self, api_client, property_obj, buyer):
        from apps.accounts.models import KYCProfile
        buyer.kyc.status = KYCProfile.Status.APPROVED
        buyer.kyc.save()
        from rest_framework_simplejwt.tokens import RefreshToken
        token = RefreshToken.for_user(buyer)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        with patch("apps.escrow.views.MpesaClient") as m:
            m.return_value.stk_push.return_value = {"CheckoutRequestID": "ws_123"}
            r = api_client.post("/api/v1/escrow/initiate/",
                                {"property_id": str(property_obj.id)})
        assert r.status_code == 201
        assert r.data["status"] == "INITIATED"
        assert r.data["amount_kes"] == 5_000_000

    def test_double_escrow_rejected(self, api_client, property_obj, buyer, seller):
        from apps.accounts.models import KYCProfile
        buyer.kyc.status = KYCProfile.Status.APPROVED
        buyer.kyc.save()
        EscrowTransaction.objects.create(
            property=property_obj, buyer=buyer, seller=seller,
            amount_kes=5_000_000, platform_fee_kes=75_000,
        )
        from rest_framework_simplejwt.tokens import RefreshToken
        token = RefreshToken.for_user(buyer)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        r = api_client.post("/api/v1/escrow/initiate/",
                            {"property_id": str(property_obj.id)})
        assert r.status_code == 400


@pytest.mark.django_db
class TestMpesaCallback:
    def test_success_funds_transaction(self, api_client, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller)
        t.mpesa_checkout_request_id = "ws_test_123"
        t.save()
        r = api_client.post("/api/v1/escrow/mpesa/callback/", {
            "Body": {"stkCallback": {"ResultCode": 0, "CheckoutRequestID": "ws_test_123"}}
        }, format="json")
        assert r.status_code == 200
        t.refresh_from_db()
        assert t.status == "FUNDED"

    def test_failed_payment_unchanged(self, api_client, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller)
        t.mpesa_checkout_request_id = "ws_fail_456"
        t.save()
        r = api_client.post("/api/v1/escrow/mpesa/callback/", {
            "Body": {"stkCallback": {"ResultCode": 1032, "CheckoutRequestID": "ws_fail_456"}}
        }, format="json")
        assert r.status_code == 200
        t.refresh_from_db()
        assert t.status == "INITIATED"


@pytest.mark.django_db
class TestEscrowStatusView:
    def test_third_party_blocked(self, property_obj, buyer, seller):
        from django.contrib.auth import get_user_model
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework.test import APIClient
        User = get_user_model()
        stranger = User.objects.create_user(
            email="stranger@test.com", phone="0700000088",
            first_name="S", last_name="T", password="x",
        )
        t = _txn(property_obj, buyer, seller)
        c = APIClient()
        token = RefreshToken.for_user(stranger)
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        r = c.get(f"/api/v1/escrow/{t.id}/status/")
        assert r.status_code == 403
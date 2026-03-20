# apps/escrow/tests.py  (state machine section — replaces existing tests)
#
# MIGRATION NOTE:
#   All tests previously catching `transitions.MachineError` now catch
#   `apps.escrow.state_machine.InvalidTransitionError` instead.
#   Everything else is identical.

import pytest
from apps.escrow.models import EscrowTransaction
from apps.escrow.state_machine import EscrowStateMachine, InvalidTransitionError


def _txn(property_obj, buyer, seller, status="INITIATED"):
    return EscrowTransaction.objects.create(
        property=property_obj, buyer=buyer, seller=seller,
        amount_kes=5_000_000, platform_fee_kes=75_000, status=status,
        mpesa_checkout_request_id="ws_test_123",  # required by fund() guard
    )


@pytest.mark.django_db
class TestStateMachine:

    # ── Happy path ────────────────────────────────────────────────────────────

    def test_fund(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller)
        EscrowStateMachine(t).fund()
        assert t.status == "FUNDED"

    def test_full_happy_path(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller)
        m = EscrowStateMachine(t)
        m.fund()
        m.start_search()
        m.sign_agreement()
        m.board_approval()
        m.transfer_title()
        m.complete()
        assert t.status == "COMPLETED"

    def test_dispute_from_funded(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller, status="FUNDED")
        EscrowStateMachine(t).dispute()
        assert t.status == "DISPUTED"

    def test_dispute_from_search_certificate(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller, status="SEARCH_CERTIFICATE")
        EscrowStateMachine(t).dispute()
        assert t.status == "DISPUTED"

    def test_dispute_from_sale_agreement(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller, status="SALE_AGREEMENT")
        EscrowStateMachine(t).dispute()
        assert t.status == "DISPUTED"

    def test_refund_from_disputed(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller, status="DISPUTED")
        EscrowStateMachine(t).refund()
        assert t.status == "REFUNDED"

    def test_refund_from_initiated(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller, status="INITIATED")
        EscrowStateMachine(t).refund()
        assert t.status == "REFUNDED"

    # ── Invalid transitions ───────────────────────────────────────────────────

    def test_invalid_transition_raises(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller, status="COMPLETED")
        with pytest.raises(InvalidTransitionError):
            EscrowStateMachine(t).fund()

    def test_dispute_not_allowed_from_completed(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller, status="COMPLETED")
        with pytest.raises(InvalidTransitionError):
            EscrowStateMachine(t).dispute()

    def test_dispute_not_allowed_from_title_transfer(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller, status="TITLE_TRANSFER")
        with pytest.raises(InvalidTransitionError):
            EscrowStateMachine(t).dispute()

    def test_complete_not_allowed_from_funded(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller, status="FUNDED")
        with pytest.raises(InvalidTransitionError):
            EscrowStateMachine(t).complete()

    def test_unknown_trigger_raises(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller)
        with pytest.raises(InvalidTransitionError, match="Unknown trigger"):
            EscrowStateMachine(t).trigger("fly_to_moon")

    # ── Error messages are informative ────────────────────────────────────────

    def test_invalid_transition_error_message_names_state(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller, status="COMPLETED")
        with pytest.raises(InvalidTransitionError, match="COMPLETED"):
            EscrowStateMachine(t).fund()

    def test_invalid_transition_error_message_names_trigger(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller, status="COMPLETED")
        with pytest.raises(InvalidTransitionError, match="fund"):
            EscrowStateMachine(t).fund()

    # ── Guard conditions ──────────────────────────────────────────────────────

    def test_fund_guard_requires_mpesa_id(self, property_obj, buyer, seller):
        """fund() should fail if no M-Pesa checkout ID is recorded."""
        t = EscrowTransaction.objects.create(
            property=property_obj, buyer=buyer, seller=seller,
            amount_kes=5_000_000, platform_fee_kes=75_000,
            status="INITIATED",
            mpesa_checkout_request_id="",  # missing
        )
        with pytest.raises(InvalidTransitionError, match="M-Pesa"):
            EscrowStateMachine(t).fund()

    def test_fund_guard_passes_with_mpesa_id(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller)  # has mpesa_checkout_request_id
        EscrowStateMachine(t).fund()
        assert t.status == "FUNDED"

    # ── Trigger by name ───────────────────────────────────────────────────────

    def test_trigger_by_name(self, property_obj, buyer, seller):
        """machine.trigger('fund') should work identically to machine.fund()"""
        t = _txn(property_obj, buyer, seller)
        EscrowStateMachine(t).trigger("fund")
        assert t.status == "FUNDED"

    # ── State property ────────────────────────────────────────────────────────

    def test_state_property_reflects_transaction(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller, status="SALE_AGREEMENT")
        m = EscrowStateMachine(t)
        assert m.state == "SALE_AGREEMENT"

    def test_state_property_updates_after_transition(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller)
        m = EscrowStateMachine(t)
        m.fund()
        assert m.state == "FUNDED"

    # ── DB persistence ────────────────────────────────────────────────────────

    def test_transition_persisted_to_db(self, property_obj, buyer, seller):
        t = _txn(property_obj, buyer, seller)
        EscrowStateMachine(t).fund()
        t.refresh_from_db()
        assert t.status == "FUNDED"

    # ── Audit log ─────────────────────────────────────────────────────────────

    def test_audit_event_created_on_transition(self, property_obj, buyer, seller):
        from apps.audit.models import AuditEvent
        t = _txn(property_obj, buyer, seller)
        EscrowStateMachine(t).fund()
        event = AuditEvent.objects.filter(
            action="ESCROW_FUNDED",
            resource_id=str(t.id),
        ).first()
        assert event is not None

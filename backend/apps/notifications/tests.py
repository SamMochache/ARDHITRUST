# apps/notifications/tests.py
import pytest
from unittest.mock import patch
from apps.notifications.tasks import (
    send_kyc_status_notification,
    send_welcome_email,
    send_verification_complete_notification,
    send_escrow_step_notification,
)


@pytest.mark.django_db
class TestNotificationTasks:
    """Tasks run synchronously thanks to CELERY_TASK_ALWAYS_EAGER=True in test settings."""

    def test_kyc_approved_notification(self, buyer):
        # Should not raise — email goes to console backend in test
        send_kyc_status_notification(str(buyer.id), "APPROVED")

    def test_kyc_rejected_notification(self, buyer):
        send_kyc_status_notification(str(buyer.id), "REJECTED")

    def test_kyc_unknown_user_safe(self, db):
        # Should log error but not raise
        send_kyc_status_notification("00000000-0000-0000-0000-000000000000", "APPROVED")

    def test_welcome_email(self, buyer):
        send_welcome_email(str(buyer.id))

    def test_welcome_email_unknown_user_safe(self, db):
        send_welcome_email("00000000-0000-0000-0000-000000000000")

    def test_verification_complete_active(self, seller, property_obj):
        send_verification_complete_notification(
            str(seller.id), str(property_obj.id), "ACTIVE"
        )

    def test_verification_complete_suspended(self, seller, property_obj):
        send_verification_complete_notification(
            str(seller.id), str(property_obj.id), "SUSPENDED"
        )

    def test_escrow_step_funded(self, buyer, seller):
        send_escrow_step_notification(str(buyer.id), str(seller.id), "FUNDED")

    def test_escrow_step_completed(self, buyer, seller):
        send_escrow_step_notification(str(buyer.id), str(seller.id), "COMPLETED")

    def test_escrow_step_unknown_step(self, buyer, seller):
        send_escrow_step_notification(str(buyer.id), str(seller.id), "UNKNOWN_STEP")
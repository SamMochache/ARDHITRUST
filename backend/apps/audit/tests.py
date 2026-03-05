# apps/audit/tests.py
import pytest
from apps.audit.models import AuditEvent


@pytest.mark.django_db
class TestAuditEvent:
    def test_log_creates_record(self, db):
        e = AuditEvent.log(
            actor=None, action="TEST_ACTION",
            resource_type="TestResource", resource_id="abc-123",
            metadata={"key": "value"},
        )
        assert e.pk is not None
        assert e.action == "TEST_ACTION"

    def test_payload_hash_computed(self, db):
        e = AuditEvent.log(
            actor=None, action="HASH_TEST",
            resource_type="T", resource_id="1",
            metadata={"amount": 500},
        )
        assert len(e.payload_hash) == 64

    def test_immutable_on_update(self, db):
        e = AuditEvent.log(
            actor=None, action="IMMUTABLE",
            resource_type="T", resource_id="2",
        )
        with pytest.raises(PermissionError, match="immutable"):
            e.metadata = {"tampered": True}
            e.save()

    def test_log_with_actor(self, db, buyer):
        e = AuditEvent.log(
            actor=buyer, action="USER_ACTION",
            resource_type="CustomUser", resource_id=str(buyer.id),
        )
        assert e.actor_id == buyer.id

    def test_empty_metadata_default(self, db):
        e = AuditEvent.log(
            actor=None, action="A", resource_type="T", resource_id="1",
        )
        assert e.metadata == {}

    def test_ordering_newest_first(self, db):
        AuditEvent.log(actor=None, action="A1", resource_type="T", resource_id="1")
        AuditEvent.log(actor=None, action="A2", resource_type="T", resource_id="2")
        events = list(AuditEvent.objects.all())
        assert events[0].action == "A2"
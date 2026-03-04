# apps/audit/models.py
import uuid, hashlib, json
from django.db import models

class AuditEvent(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor_id      = models.UUIDField(null=True, blank=True)
    action        = models.CharField(max_length=100, db_index=True)
    resource_type = models.CharField(max_length=100, db_index=True)
    resource_id   = models.CharField(max_length=200)
    ip_address    = models.GenericIPAddressField(null=True, blank=True)
    user_agent    = models.CharField(max_length=500, blank=True)
    metadata      = models.JSONField(default=dict)
    payload_hash  = models.CharField(max_length=64, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_event"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.pk:
            raise PermissionError("AuditEvent records are immutable.")
        self.payload_hash = hashlib.sha256(
            json.dumps(self.metadata, sort_keys=True, default=str).encode()
        ).hexdigest()
        super().save(*args, **kwargs)

    @classmethod
    def log(cls, actor, action: str, resource_type: str, resource_id: str, metadata: dict = None):
        return cls.objects.create(
            actor_id=actor.id if actor else None,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            metadata=metadata or {},
        )
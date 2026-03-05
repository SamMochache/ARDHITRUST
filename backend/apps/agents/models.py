# apps/agents/models.py
import uuid
from django.db import models

class AgentRun(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_name  = models.CharField(max_length=100, db_index=True)
    input_hash  = models.CharField(max_length=64, db_index=True)
    output_json = models.JSONField(default=dict)
    duration_ms = models.IntegerField(default=0)
    tokens_used = models.IntegerField(default=0)
    error       = models.TextField(null=True, blank=True)
    property_id = models.UUIDField(null=True, blank=True, db_index=True)
    user_id     = models.UUIDField(null=True, blank=True, db_index=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "agents_run"
        indexes = [models.Index(fields=["agent_name", "input_hash"])]
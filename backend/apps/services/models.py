# apps/services/models.py
import uuid
from django.db import models

class ServiceRequest(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property     = models.ForeignKey("properties.Property", on_delete=models.PROTECT)
    requester    = models.ForeignKey("accounts.CustomUser", on_delete=models.PROTECT)
    service_type = models.CharField(max_length=20, choices=[
        ("VALUATION","Valuation"), ("SURVEY","Survey"), ("DUE_DILIGENCE","Due Diligence")
    ])
    status       = models.CharField(max_length=20, default="OPEN")
    notes        = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

class Quote(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request        = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name="quotes")
    provider       = models.ForeignKey("accounts.CustomUser", on_delete=models.PROTECT)
    amount_kes     = models.IntegerField()
    details        = models.TextField()
    estimated_days = models.IntegerField()
    accepted       = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)
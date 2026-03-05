# apps/verification/models.py
import uuid
from django.db import models

class VerificationRequest(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property     = models.ForeignKey("properties.Property", on_delete=models.PROTECT,
                                     related_name="verification_requests")
    requested_by = models.ForeignKey("accounts.CustomUser", on_delete=models.PROTECT)
    status       = models.CharField(max_length=20, default="PENDING")
    created_at   = models.DateTimeField(auto_now_add=True)

class VerificationResult(models.Model):
    id                   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request              = models.OneToOneField(VerificationRequest, on_delete=models.CASCADE,
                                                related_name="result")
    ownership_confirmed  = models.BooleanField(default=False)
    registered_owner     = models.CharField(max_length=200, blank=True)
    encumbrances_json    = models.JSONField(default=list)
    caveat_present       = models.BooleanField(default=False)
    rates_cleared        = models.BooleanField(default=False)
    created_at           = models.DateTimeField(auto_now_add=True)
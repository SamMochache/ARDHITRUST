import uuid
from django.db import models

class EscrowTransaction(models.Model):
    id                       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property                 = models.OneToOneField("properties.Property", on_delete=models.PROTECT)
    buyer                    = models.ForeignKey("accounts.CustomUser", on_delete=models.PROTECT,
                                                 related_name="purchases")
    seller                   = models.ForeignKey("accounts.CustomUser", on_delete=models.PROTECT,
                                                  related_name="sales")
    amount_kes               = models.BigIntegerField()
    platform_fee_kes         = models.IntegerField()   # 1.5%
    status                   = models.CharField(max_length=30, default="INITIATED", db_index=True)
    mpesa_checkout_request_id = models.CharField(max_length=200, blank=True)
    funds_released_at        = models.DateTimeField(null=True, blank=True)
    created_at               = models.DateTimeField(auto_now_add=True)
    updated_at               = models.DateTimeField(auto_now=True)
import uuid
from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from encrypted_model_fields.fields import EncryptedCharField

class PropertyType(models.TextChoices):
    RESIDENTIAL  = "RESIDENTIAL"
    AGRICULTURAL = "AGRICULTURAL"
    COMMERCIAL   = "COMMERCIAL"
    INDUSTRIAL   = "INDUSTRIAL"

class PropertyStatus(models.TextChoices):
    DRAFT                = "DRAFT"
    VERIFICATION_PENDING = "VERIFICATION_PENDING"
    ACTIVE               = "ACTIVE"
    UNDER_OFFER          = "UNDER_OFFER"
    SOLD                 = "SOLD"
    SUSPENDED            = "SUSPENDED"

class Property(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller        = models.ForeignKey("accounts.CustomUser", on_delete=models.PROTECT,
                                      related_name="listings")
    title         = models.CharField(max_length=200)
    description   = models.TextField()
    county        = models.CharField(max_length=100, db_index=True)
    sub_county    = models.CharField(max_length=100, blank=True)
    area_name     = models.CharField(max_length=200)
    latitude      = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude     = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # LR Number — plain for search, encrypted copy for verification calls
    lr_number           = models.CharField(max_length=100, db_index=True)
    lr_number_encrypted = EncryptedCharField(max_length=200)

    property_type    = models.CharField(max_length=20, choices=PropertyType.choices, db_index=True)
    size_acres       = models.DecimalField(max_digits=10, decimal_places=4, db_index=True)
    price_kes        = models.BigIntegerField(db_index=True)
    price_negotiable = models.BooleanField(default=False)
    status           = models.CharField(max_length=30, choices=PropertyStatus.choices,
                                        default=PropertyStatus.DRAFT, db_index=True)
    is_verified_pro  = models.BooleanField(default=False)
    trust_score      = models.IntegerField(default=0)   # 0–100
    last_verified_at = models.DateTimeField(null=True, blank=True)

    search_vector = SearchVectorField(null=True, blank=True)
    embedding     = models.TextField(null=True, blank=True)  # pgvector JSON array

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "properties_property"
        indexes = [
            GinIndex(fields=["search_vector"]),
            models.Index(fields=["county", "property_type", "status"]),
            models.Index(fields=["price_kes"]),
            models.Index(fields=["size_acres"]),
        ]
        ordering = ["-created_at"]
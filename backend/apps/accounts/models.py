import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField

class UserRole(models.TextChoices):
    BUYER    = "BUYER"
    SELLER   = "SELLER"
    ADMIN    = "ADMIN"
    SURVEYOR = "SURVEYOR"
    VALUER   = "VALUER"

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email       = models.EmailField(unique=True)
    phone       = models.CharField(max_length=15, unique=True)
    first_name  = models.CharField(max_length=100)
    last_name   = models.CharField(max_length=100)
    role        = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.BUYER)

    # PII — AES-256 encrypted at column level
    national_id_encrypted = EncryptedCharField(max_length=20, blank=True)

    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    email_verified  = models.BooleanField(default=False)
    phone_verified  = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["phone", "first_name", "last_name"]

    class Meta:
        db_table = "accounts_user"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
        ]


class KYCProfile(models.Model):
    class Status(models.TextChoices):
        PENDING   = "PENDING"
        IN_REVIEW = "IN_REVIEW"
        APPROVED  = "APPROVED"
        REJECTED  = "REJECTED"

    user              = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="kyc")
    status            = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    iprs_verified     = models.BooleanField(default=False)
    kra_verified      = models.BooleanField(default=False)
    kra_pin_encrypted = EncryptedCharField(max_length=20, blank=True)
    id_front_s3_key   = models.CharField(max_length=500, blank=True)
    id_back_s3_key    = models.CharField(max_length=500, blank=True)
    rejection_reason  = models.TextField(blank=True)
    submitted_at      = models.DateTimeField(null=True, blank=True)
    reviewed_at       = models.DateTimeField(null=True, blank=True)
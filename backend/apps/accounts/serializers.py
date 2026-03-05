# apps/accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, KYCProfile


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label="Confirm password")
    role      = serializers.ChoiceField(
        choices=["BUYER", "SELLER"], default="BUYER"
    )

    class Meta:
        model  = CustomUser
        fields = ["email", "phone", "first_name", "last_name", "role", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        # Auto-create empty KYC profile
        KYCProfile.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    kyc_status = serializers.SerializerMethodField()

    class Meta:
        model  = CustomUser
        fields = [
            "id", "email", "phone", "first_name", "last_name",
            "role", "email_verified", "phone_verified", "kyc_status", "created_at",
        ]
        read_only_fields = fields

    def get_kyc_status(self, obj):
        try:
            return obj.kyc.status
        except KYCProfile.DoesNotExist:
            return None


class KYCSubmitSerializer(serializers.Serializer):
    national_id   = serializers.CharField(max_length=20)
    kra_pin       = serializers.CharField(max_length=20)
    id_front_key  = serializers.CharField(max_length=500, help_text="S3 key from presigned upload")
    id_back_key   = serializers.CharField(max_length=500, help_text="S3 key from presigned upload")

    def validate_national_id(self, value):
        # Kenya national IDs are 7-8 digits
        if not value.isdigit() or not (7 <= len(value) <= 8):
            raise serializers.ValidationError("National ID must be 7-8 digits.")
        return value

    def validate_kra_pin(self, value):
        # Kenya KRA PINs: letter + 9 digits + letter, e.g. A123456789Z
        import re
        if not re.match(r'^[A-Z]\d{9}[A-Z]$', value.upper()):
            raise serializers.ValidationError("KRA PIN format invalid (e.g. A123456789Z).")
        return value.upper()


class KYCStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model  = KYCProfile
        fields = ["status", "iprs_verified", "kra_verified", "rejection_reason",
                  "submitted_at", "reviewed_at"]
        read_only_fields = fields
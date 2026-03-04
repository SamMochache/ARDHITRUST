# apps/properties/serializers.py
from rest_framework import serializers
from core.validators import validate_lr_number
from .models import Property

class PropertyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            "title", "description", "county", "sub_county", "area_name",
            "lr_number", "property_type", "size_acres",
            "price_kes", "price_negotiable", "latitude", "longitude",
        ]

    def validate_lr_number(self, value):
        validate_lr_number(value)          # checks format regex
        return value.upper().strip()

    def validate_size_acres(self, value):
        if value <= 0 or value > 10000:
            raise serializers.ValidationError("Size must be between 0 and 10,000 acres.")
        return value

    def create(self, validated_data):
        validated_data["lr_number_encrypted"] = validated_data["lr_number"]
        validated_data["seller"] = self.context["request"].user
        validated_data["status"] = "VERIFICATION_PENDING"
        prop = super().create(validated_data)
        from apps.verification.tasks import initiate_ardhisasa_check
        initiate_ardhisasa_check.delay(str(prop.id))
        return prop

class PropertyListSerializer(serializers.ModelSerializer):
    last_verified = serializers.SerializerMethodField()
    price         = serializers.SerializerMethodField()
    size          = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id", "title", "area_name", "county", "price", "size",
            "property_type", "is_verified_pro", "trust_score",
            "last_verified", "status",
        ]

    def get_last_verified(self, obj):
        if not obj.last_verified_at:
            return "Not yet verified"
        from django.utils.timesince import timesince
        return f"{timesince(obj.last_verified_at)} ago"

    def get_price(self, obj): return f"KES {obj.price_kes:,}"
    def get_size(self, obj):  return f"{obj.size_acres} Acres"
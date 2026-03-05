# apps/properties/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display   = ["title", "county", "property_type", "trust_score_badge",
                       "status", "price_display", "seller", "created_at"]
    list_filter    = ["status", "county", "property_type", "is_verified_pro"]
    search_fields  = ["title", "area_name", "county", "lr_number"]
    ordering       = ["-created_at"]
    readonly_fields = ["id", "trust_score", "last_verified_at", "search_vector",
                        "embedding", "created_at", "updated_at"]
    exclude        = ["lr_number_encrypted"]

    def trust_score_badge(self, obj):
        colour = "green" if obj.trust_score >= 70 else ("orange" if obj.trust_score >= 40 else "red")
        return format_html(
            '<span style="color:{};font-weight:bold">{}</span>', colour, obj.trust_score
        )
    trust_score_badge.short_description = "Trust"

    def price_display(self, obj):
        return f"KES {obj.price_kes:,}"
    price_display.short_description = "Price"
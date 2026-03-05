# apps/accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, KYCProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display   = ["email", "first_name", "last_name", "role", "kyc_status_badge",
                       "email_verified", "is_active", "created_at"]
    list_filter    = ["role", "is_active", "email_verified"]
    search_fields  = ["email", "phone", "first_name", "last_name"]
    ordering       = ["-created_at"]
    readonly_fields = ["id", "created_at", "last_login"]

    fieldsets = (
        (None, {"fields": ("id", "email", "phone", "password")}),
        ("Personal", {"fields": ("first_name", "last_name", "role")}),
        ("Status", {"fields": ("is_active", "is_staff", "email_verified", "phone_verified")}),
        ("Timestamps", {"fields": ("created_at", "last_login")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone", "first_name", "last_name", "role", "password1", "password2"),
        }),
    )

    # Never show encrypted PII in admin
    exclude = ["national_id_encrypted", "user_permissions", "groups"]

    def kyc_status_badge(self, obj):
        try:
            s = obj.kyc.status
        except KYCProfile.DoesNotExist:
            return format_html('<span style="color:grey">No KYC</span>')
        colours = {
            "APPROVED": "green", "REJECTED": "red",
            "IN_REVIEW": "orange", "PENDING": "grey",
        }
        return format_html(
            '<span style="color:{}">{}</span>', colours.get(s, "grey"), s
        )
    kyc_status_badge.short_description = "KYC"

    def has_delete_permission(self, request, obj=None):
        return False  # Deactivate only — never delete users


@admin.register(KYCProfile)
class KYCProfileAdmin(admin.ModelAdmin):
    list_display   = ["user", "status_badge", "iprs_verified", "kra_verified", "submitted_at"]
    list_filter    = ["status"]
    search_fields  = ["user__email", "user__phone"]
    readonly_fields = ["user", "iprs_verified", "kra_verified", "submitted_at", "reviewed_at"]
    exclude        = ["kra_pin_encrypted"]

    actions = ["bulk_approve", "bulk_reject"]

    def status_badge(self, obj):
        colours = {
            "APPROVED": "green", "REJECTED": "red",
            "IN_REVIEW": "orange", "PENDING": "grey",
        }
        return format_html(
            '<span style="color:{}">{}</span>', colours.get(obj.status, "grey"), obj.status
        )
    status_badge.short_description = "Status"

    def bulk_approve(self, request, queryset):
        queryset.filter(status="IN_REVIEW").update(status="APPROVED")
    bulk_approve.short_description = "Approve selected KYC profiles"

    def bulk_reject(self, request, queryset):
        queryset.filter(status="IN_REVIEW").update(status="REJECTED")
    bulk_reject.short_description = "Reject selected KYC profiles"
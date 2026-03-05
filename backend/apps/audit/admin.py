# apps/audit/admin.py
from django.contrib import admin
from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display    = ["action", "resource_type", "resource_id", "actor_id", "created_at"]
    list_filter     = ["action", "resource_type"]
    search_fields   = ["action", "resource_type", "resource_id"]
    ordering        = ["-created_at"]
    readonly_fields = ["id", "actor_id", "action", "resource_type", "resource_id",
                        "ip_address", "user_agent", "metadata", "payload_hash", "created_at"]

    def has_add_permission(self, request):
        return False  # immutable — only created via AuditEvent.log()

    def has_change_permission(self, request, obj=None):
        return False  # immutable

    def has_delete_permission(self, request, obj=None):
        return False  # compliance records — never delete
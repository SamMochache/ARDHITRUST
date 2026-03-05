# apps/agents/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import AgentRun


@admin.register(AgentRun)
class AgentRunAdmin(admin.ModelAdmin):
    list_display    = ["agent_name", "status_badge", "tokens_used",
                        "duration_ms", "property_id", "created_at"]
    list_filter     = ["agent_name"]
    search_fields   = ["agent_name", "property_id", "user_id"]
    ordering        = ["-created_at"]
    readonly_fields = ["id", "agent_name", "input_hash", "output_json",
                        "duration_ms", "tokens_used", "error",
                        "property_id", "user_id", "created_at"]

    def status_badge(self, obj):
        if obj.error:
            return format_html('<span style="color:red;font-weight:bold">ERROR</span>')
        return format_html('<span style="color:green;font-weight:bold">OK</span>')
    status_badge.short_description = "Status"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
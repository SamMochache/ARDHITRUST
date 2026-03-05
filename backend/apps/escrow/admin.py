# apps/escrow/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import EscrowTransaction

STATUS_COLOURS = {
    "INITIATED":          "grey",
    "FUNDED":             "blue",
    "SEARCH_CERTIFICATE": "orange",
    "SALE_AGREEMENT":     "orange",
    "LAND_BOARD_APPROVAL": "orange",
    "TITLE_TRANSFER":     "darkorange",
    "COMPLETED":          "green",
    "DISPUTED":           "red",
    "REFUNDED":           "purple",
}


@admin.register(EscrowTransaction)
class EscrowTransactionAdmin(admin.ModelAdmin):
    list_display    = ["id_short", "property", "buyer", "seller",
                        "status_badge", "amount_display", "created_at"]
    list_filter     = ["status"]
    search_fields   = ["buyer__email", "seller__email", "property__title"]
    ordering        = ["-created_at"]
    readonly_fields = ["id", "property", "buyer", "seller", "amount_kes",
                        "platform_fee_kes", "status", "mpesa_checkout_request_id",
                        "funds_released_at", "created_at", "updated_at"]

    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = "ID"

    def status_badge(self, obj):
        colour = STATUS_COLOURS.get(obj.status, "grey")
        return format_html(
            '<span style="color:{};font-weight:bold">{}</span>', colour, obj.status
        )
    status_badge.short_description = "Status"

    def amount_display(self, obj):
        return f"KES {obj.amount_kes:,}"
    amount_display.short_description = "Amount"

    def has_add_permission(self, request):
        return False  # escrow only created via API

    def has_delete_permission(self, request, obj=None):
        return False  # financial records — never delete
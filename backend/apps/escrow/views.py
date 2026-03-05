# apps/escrow/views.py
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsKYCApproved
from apps.audit.models import AuditEvent
from apps.properties.models import Property
from .models import EscrowTransaction
from .services.mpesa_client import MpesaClient
from .state_machine import EscrowStateMachine


class EscrowInitiateView(APIView):
    """POST /api/v1/escrow/initiate/ — buyer starts escrow."""
    permission_classes = [IsKYCApproved]

    def post(self, request):
        property_id = request.data.get("property_id")
        try:
            prop = Property.objects.get(id=property_id, status="ACTIVE")
        except Property.DoesNotExist:
            return Response({"detail": "Property not found or not available."},
                            status=status.HTTP_404_NOT_FOUND)

        if prop.seller == request.user:
            return Response({"detail": "You cannot buy your own listing."},
                            status=status.HTTP_400_BAD_REQUEST)

        if EscrowTransaction.objects.filter(property=prop).exists():
            return Response({"detail": "Escrow already exists for this property."},
                            status=status.HTTP_400_BAD_REQUEST)

        platform_fee = int(prop.price_kes * 0.015)
        txn = EscrowTransaction.objects.create(
            property=prop,
            buyer=request.user,
            seller=prop.seller,
            amount_kes=prop.price_kes,
            platform_fee_kes=platform_fee,
            status="INITIATED",
        )

        # Trigger STK push
        try:
            mpesa_resp = MpesaClient().stk_push(
                phone=request.user.phone,
                amount=prop.price_kes + platform_fee,
                account_ref=str(txn.id)[:12],
                desc="ArdhiTrust Escrow",
            )
            txn.mpesa_checkout_request_id = mpesa_resp.get("CheckoutRequestID", "")
            txn.save(update_fields=["mpesa_checkout_request_id"])
        except Exception as e:
            # Don't fail — user can retry payment
            pass

        AuditEvent.log(
            actor=request.user, action="ESCROW_INITIATED",
            resource_type="EscrowTransaction", resource_id=str(txn.id),
            metadata={"property_id": str(prop.id), "amount": prop.price_kes},
        )

        prop.status = "UNDER_OFFER"
        prop.save(update_fields=["status"])

        return Response({
            "escrow_id": str(txn.id),
            "status": txn.status,
            "amount_kes": txn.amount_kes,
            "platform_fee_kes": txn.platform_fee_kes,
            "mpesa_checkout_request_id": txn.mpesa_checkout_request_id,
        }, status=status.HTTP_201_CREATED)


class EscrowStatusView(APIView):
    """GET /api/v1/escrow/<id>/status/"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            txn = EscrowTransaction.objects.select_related("property", "buyer", "seller").get(
                id=pk
            )
        except EscrowTransaction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user not in [txn.buyer, txn.seller] and not request.user.is_staff:
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        return Response({
            "id":             str(txn.id),
            "status":         txn.status,
            "amount_kes":     txn.amount_kes,
            "platform_fee":   txn.platform_fee_kes,
            "property":       txn.property.title,
            "buyer":          txn.buyer.get_full_name(),
            "seller":         txn.seller.get_full_name(),
            "funds_released": txn.funds_released_at,
            "created_at":     txn.created_at,
        })


class EscrowAdvanceView(APIView):
    """POST /api/v1/escrow/<id>/advance/ — admin-only step advancement."""
    permission_classes = [IsAuthenticated]

    TRIGGER_MAP = {
        "INITIATED":          "fund",
        "FUNDED":             "start_search",
        "SEARCH_CERTIFICATE": "sign_agreement",
        "SALE_AGREEMENT":     "board_approval",
        "LAND_BOARD_APPROVAL": "transfer_title",
        "TITLE_TRANSFER":     "complete",
    }

    def post(self, request, pk):
        if not request.user.is_staff:
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)

        try:
            txn = EscrowTransaction.objects.get(id=pk)
        except EscrowTransaction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        trigger = self.TRIGGER_MAP.get(txn.status)
        if not trigger:
            return Response({"detail": f"No advance possible from {txn.status}."},
                            status=status.HTTP_400_BAD_REQUEST)

        machine = EscrowStateMachine(txn)
        getattr(machine, trigger)()

        return Response({"status": txn.status})


class MpesaCallbackView(APIView):
    """POST /api/v1/escrow/mpesa/callback/ — Safaricom callback (no auth)."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        body = request.data.get("Body", {})
        callback = body.get("stkCallback", {})
        result_code = callback.get("ResultCode")
        checkout_id = callback.get("CheckoutRequestID", "")

        AuditEvent.log(
            actor=None, action="MPESA_CALLBACK",
            resource_type="EscrowTransaction", resource_id=checkout_id,
            metadata={"result_code": result_code},
        )

        if result_code != 0:
            return Response({"ResultCode": 0, "ResultDesc": "Accepted"})

        try:
            txn = EscrowTransaction.objects.get(mpesa_checkout_request_id=checkout_id)
            machine = EscrowStateMachine(txn)
            machine.fund()
        except EscrowTransaction.DoesNotExist:
            pass
        except Exception:
            pass

        return Response({"ResultCode": 0, "ResultDesc": "Accepted"})
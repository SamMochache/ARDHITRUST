# apps/escrow/tasks.py — FULL REPLACEMENT
# FIX 2: process_mpesa_callback task added
#
# PROBLEM SOLVED:
#   Callback processing now happens asynchronously via Celery.
#   If DB is slow or temporarily down, the task retries — no lost payments.
#   The callback endpoint returns 200 immediately, satisfying Safaricom.

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(
    queue="payments",
    max_retries=5,
    default_retry_delay=30,
    autoretry_for=(Exception,),
    # Idempotency: if the same callback is processed twice (Safaricom resends
    # on timeout), the second run is a no-op because status is already FUNDED.
)
def process_mpesa_callback(checkout_id: str, result_code: int, raw_callback: dict):
    """
    FIX 2: Process M-Pesa STK callback asynchronously.
    Retries up to 5 times with 30s delay if DB is temporarily unavailable.
    Safe to retry — state machine won't double-fund.
    """
    from apps.escrow.models import EscrowTransaction
    from apps.escrow.state_machine import EscrowStateMachine
    from apps.audit.models import AuditEvent

    AuditEvent.log(
        actor=None, action="MPESA_CALLBACK",
        resource_type="EscrowTransaction", resource_id=checkout_id,
        metadata={"result_code": result_code},
    )

    if result_code != 0:
        logger.info(f"M-Pesa callback: payment failed for {checkout_id} (code {result_code})")
        return

    try:
        txn = EscrowTransaction.objects.select_for_update().get(
            mpesa_checkout_request_id=checkout_id
        )
    except EscrowTransaction.DoesNotExist:
        logger.error(f"M-Pesa callback: no transaction for checkout_id={checkout_id}")
        return

    if txn.status != "INITIATED":
        logger.info(f"M-Pesa callback: {checkout_id} already {txn.status}, skipping")
        return  # Idempotent — already funded

    try:
        EscrowStateMachine(txn).fund()
        logger.info(f"M-Pesa callback: funded escrow {txn.id}")
    except Exception as exc:
        logger.exception(f"M-Pesa fund transition failed for {txn.id}: {exc}")
        raise


@shared_task(queue="payments", max_retries=3, default_retry_delay=60)
def release_funds_to_seller(transaction_id: str):
    from apps.escrow.models import EscrowTransaction
    from apps.escrow.services.mpesa_client import MpesaClient
    from apps.audit.models import AuditEvent
    from django.utils import timezone

    try:
        txn = EscrowTransaction.objects.select_related("seller").get(id=transaction_id)
        payout = txn.amount_kes - txn.platform_fee_kes

        MpesaClient().b2c_payment(
            phone=txn.seller.phone,
            amount=payout,
            occasion="ArdhiTrust sale payout",
            remarks=f"Escrow {transaction_id[:8]}",
        )

        txn.funds_released_at = timezone.now()
        txn.save(update_fields=["funds_released_at"])

        AuditEvent.log(
            actor=None, action="FUNDS_RELEASED",
            resource_type="EscrowTransaction", resource_id=transaction_id,
            metadata={"payout_kes": payout, "seller": str(txn.seller.id)},
        )
        logger.info(f"Funds released for escrow {transaction_id}")

    except Exception as exc:
        logger.exception(f"Fund release failed for {transaction_id}: {exc}")
        raise
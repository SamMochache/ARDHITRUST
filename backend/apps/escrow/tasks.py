# apps/escrow/tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


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
            occasion=f"ArdhiTrust sale payout",
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
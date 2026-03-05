# apps/notifications/tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

@shared_task(queue="default", max_retries=3)
def send_kyc_status_notification(user_id: str, status: str):
    logger.info(f"[STUB] KYC notification → user {user_id}: {status}")
    # TODO: wire up Africa's Talking SMS + SES email

@shared_task(queue="default")
def send_welcome_email(user_id: str):
    logger.info(f"[STUB] Welcome email → user {user_id}")

@shared_task(queue="default")
def send_verification_complete_notification(seller_id: str, property_id: str, status: str):
    logger.info(f"[STUB] Verification complete → seller {seller_id}, property {property_id}: {status}")

@shared_task(queue="default")
def send_escrow_step_notification(buyer_id: str, seller_id: str, step: str):
    logger.info(f"[STUB] Escrow step → {step}")
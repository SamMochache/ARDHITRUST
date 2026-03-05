# apps/notifications/tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def _send_sms(phone: str, message: str) -> bool:
    """Send SMS via Africa's Talking. Returns True on success."""
    try:
        import africastalking
        from django.conf import settings
        africastalking.initialize(
            username=settings.AFRICAS_TALKING_USERNAME,
            api_key=settings.AFRICAS_TALKING_API_KEY,
        )
        sms = africastalking.SMS
        response = sms.send(message, [phone])
        recipients = response.get("SMSMessageData", {}).get("Recipients", [])
        return any(r.get("status") == "Success" for r in recipients)
    except Exception as e:
        logger.warning(f"SMS failed to {phone}: {e}")
        return False


def _send_email(to: str, subject: str, body: str) -> bool:
    """Send transactional email via Django's email backend (SES in prod)."""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        send_mail(
            subject=subject,
            message=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@ardhitrust.co.ke"),
            recipient_list=[to],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.warning(f"Email failed to {to}: {e}")
        return False


@shared_task(queue="default", max_retries=3, default_retry_delay=60)
def send_kyc_status_notification(user_id: str, status: str):
    from apps.accounts.models import CustomUser
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        logger.error(f"send_kyc_status_notification: user {user_id} not found")
        return

    messages = {
        "APPROVED": (
            "Your ArdhiTrust KYC has been approved! You can now list and purchase properties.",
            "KYC Approved — ArdhiTrust",
        ),
        "REJECTED": (
            "Your ArdhiTrust KYC was not approved. Please log in for details and resubmit.",
            "KYC Action Required — ArdhiTrust",
        ),
        "IN_REVIEW": (
            "Your ArdhiTrust KYC is under review. We'll notify you within 2 minutes.",
            "KYC Under Review — ArdhiTrust",
        ),
    }
    sms_body, email_subject = messages.get(
        status,
        (f"Your KYC status has been updated to: {status}", "KYC Update — ArdhiTrust"),
    )

    _send_sms(user.phone, sms_body)
    _send_email(user.email, email_subject, sms_body)
    logger.info(f"KYC notification sent → user {user_id}: {status}")


@shared_task(queue="default", max_retries=3)
def send_welcome_email(user_id: str):
    from apps.accounts.models import CustomUser
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return

    body = (
        f"Welcome to ArdhiTrust, {user.first_name}!\n\n"
        "Kenya's most trusted land marketplace.\n\n"
        "Complete your KYC verification to unlock buying and selling.\n\n"
        "— The ArdhiTrust Team"
    )
    _send_email(user.email, "Welcome to ArdhiTrust!", body)
    logger.info(f"Welcome email sent → {user.email}")


@shared_task(queue="default", max_retries=3)
def send_verification_complete_notification(seller_id: str, property_id: str, status: str):
    from apps.accounts.models import CustomUser
    from apps.properties.models import Property
    try:
        seller = CustomUser.objects.get(id=seller_id)
        prop   = Property.objects.get(id=property_id)
    except (CustomUser.DoesNotExist, Property.DoesNotExist):
        return

    if status == "ACTIVE":
        msg = (
            f"Great news! Your property '{prop.title}' has been verified "
            f"(Trust Score: {prop.trust_score}/100) and is now LIVE on ArdhiTrust."
        )
    else:
        msg = (
            f"Your property '{prop.title}' verification returned status: {status}. "
            "Please log in to review the details."
        )

    _send_sms(seller.phone, msg)
    _send_email(seller.email, f"Property Verification Update — {prop.title}", msg)
    logger.info(f"Verification notification sent → seller {seller_id}, property {property_id}: {status}")


@shared_task(queue="default", max_retries=3)
def send_escrow_step_notification(buyer_id: str, seller_id: str, step: str):
    from apps.accounts.models import CustomUser

    STEP_MESSAGES = {
        "FUNDED":              "Funds confirmed. The land search certificate process has begun.",
        "SEARCH_CERTIFICATE":  "Land search certificate obtained. Sale agreement being prepared.",
        "SALE_AGREEMENT":      "Sale agreement signed. Awaiting Land Board approval.",
        "LAND_BOARD_APPROVAL": "Land Board approval granted. Title transfer in progress.",
        "TITLE_TRANSFER":      "Title transfer complete. Final checks underway.",
        "COMPLETED":           "🎉 Congratulations! The transaction is complete. Funds are being released.",
        "DISPUTED":            "⚠️ A dispute has been raised on your transaction. Our team will contact you.",
        "REFUNDED":            "Your escrow funds have been refunded.",
    }
    msg = STEP_MESSAGES.get(step, f"Escrow update: {step}")

    for uid in [buyer_id, seller_id]:
        try:
            user = CustomUser.objects.get(id=uid)
            _send_sms(user.phone, f"ArdhiTrust: {msg}")
            _send_email(user.email, f"Escrow Update: {step}", msg)
        except CustomUser.DoesNotExist:
            pass

    logger.info(f"Escrow step notification sent → step {step}")
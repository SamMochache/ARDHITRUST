from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(
    bind=True, queue="verification",
    max_retries=3, default_retry_delay=60,
    autoretry_for=(ConnectionError,),
)
def process_kyc_submission(self, kyc_id: str):
    from apps.accounts.models import KYCProfile
    from apps.accounts.services.iprs_service import IPRSService
    from apps.accounts.services.kra_service import KRAService
    from apps.notifications.tasks import send_kyc_status_notification
    from apps.audit.models import AuditEvent
    from django.utils import timezone

    try:
        kyc = KYCProfile.objects.select_related("user").get(id=kyc_id)
        kyc.status = KYCProfile.Status.IN_REVIEW
        kyc.save(update_fields=["status"])

        iprs_result = IPRSService().verify(
            national_id=kyc.user.national_id_encrypted,
            first_name=kyc.user.first_name,
            last_name=kyc.user.last_name,
        )
        kra_result = KRAService().verify(
            kra_pin=kyc.kra_pin_encrypted,
            national_id=kyc.user.national_id_encrypted,
        )

        kyc.iprs_verified = iprs_result.verified
        kyc.kra_verified  = kra_result.verified
        kyc.status = (
            KYCProfile.Status.APPROVED
            if kyc.iprs_verified and kyc.kra_verified
            else KYCProfile.Status.REJECTED
        )
        if kyc.status == KYCProfile.Status.REJECTED:
            kyc.rejection_reason = (
                f"IPRS: {'PASS' if kyc.iprs_verified else 'FAIL'}, "
                f"KRA: {'PASS' if kyc.kra_verified else 'FAIL'}"
            )

        kyc.reviewed_at = timezone.now()
        kyc.save()

        send_kyc_status_notification.delay(str(kyc.user.id), kyc.status)
        AuditEvent.log(
            actor=None, action="KYC_PROCESSED",
            resource_type="KYCProfile", resource_id=kyc_id,
            metadata={"status": kyc.status},
        )

    except KYCProfile.DoesNotExist:
        logger.error(f"KYC {kyc_id} not found")
    except Exception as exc:
        raise self.retry(exc=exc)
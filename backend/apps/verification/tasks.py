from celery import shared_task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

@shared_task(bind=True, queue="verification", max_retries=5, default_retry_delay=120)
def initiate_ardhisasa_check(self, property_id: str):
    from apps.properties.models import Property
    from apps.verification.models import VerificationRequest, VerificationResult
    from apps.verification.services.ardhisasa_client import ArdhisasaClient
    from apps.verification.services.trust_score import calculate_trust_score
    from apps.notifications.tasks import send_verification_complete_notification
    from apps.audit.models import AuditEvent
    from django.utils import timezone

    try:
        prop = Property.objects.get(id=property_id)
        req  = VerificationRequest.objects.create(
            property=prop, requested_by=prop.seller, status="IN_PROGRESS"
        )

        result = ArdhisasaClient().land_search(prop.lr_number)

        ver = VerificationResult.objects.create(
            request=req,
            ownership_confirmed=result.ownership_confirmed,
            registered_owner=result.registered_owner,
            encumbrances_json=result.encumbrances,
            caveat_present=result.caveat_present,
            rates_cleared=result.rates_cleared,
        )

        trust_score = calculate_trust_score(ver, prop)
        prop.trust_score      = trust_score
        prop.last_verified_at = timezone.now()
        prop.status = "ACTIVE" if result.ownership_confirmed else "SUSPENDED"
        prop.save(update_fields=["trust_score", "last_verified_at", "status"])

        # Kick off the AI title analysis
        from apps.agents.tasks import run_title_intelligence_agent
        run_title_intelligence_agent.delay(property_id)

        send_verification_complete_notification.delay(
            str(prop.seller.id), property_id, prop.status
        )
        AuditEvent.log(
            actor=prop.seller, action="PROPERTY_VERIFIED",
            resource_type="Property", resource_id=property_id,
            metadata={"trust_score": trust_score, "status": prop.status},
        )

    except Exception as exc:
        logger.exception(f"Verification failed for {property_id}: {exc}")
        raise self.retry(exc=exc)
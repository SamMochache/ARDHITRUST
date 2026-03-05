# apps/agents/tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(queue="ai_agents", max_retries=2, default_retry_delay=30)
def run_title_intelligence_agent(property_id: str):
    from apps.properties.models import Property
    from apps.verification.models import VerificationResult
    from apps.agents.title_intelligence_agent import TitleIntelligenceAgent

    try:
        prop = Property.objects.select_related("seller").get(id=property_id)
        ver  = (
            VerificationResult.objects
            .filter(request__property=prop)
            .order_by("-created_at")
            .first()
        )
        if not ver:
            logger.warning(f"No verification result for property {property_id}")
            return

        property_data = {
            "id": str(prop.id), "title": prop.title,
            "county": prop.county, "property_type": prop.property_type,
            "size_acres": float(prop.size_acres), "price_kes": prop.price_kes,
            "lr_number": prop.lr_number,
        }
        verification_result = {
            "ownership_confirmed": ver.ownership_confirmed,
            "registered_owner":    ver.registered_owner,
            "encumbrances":        ver.encumbrances_json,
            "caveat_present":      ver.caveat_present,
            "rates_cleared":       ver.rates_cleared,
        }

        agent  = TitleIntelligenceAgent()
        output = agent.run(
            property_data=property_data,
            verification_result=verification_result,
            property_id=property_id,
        )

        # Update trust score if agent returned a higher-confidence score
        if output.get("trust_score") and not output.get("error"):
            prop.trust_score = output["trust_score"]
            prop.save(update_fields=["trust_score"])
            logger.info(f"TitleIntelligenceAgent updated trust_score={output['trust_score']} for {property_id}")

    except Exception as exc:
        logger.exception(f"TitleIntelligenceAgent failed for {property_id}: {exc}")
        raise


@shared_task(queue="ai_agents", max_retries=2)
def run_fraud_detection(user_id: str, context: dict = None):
    """Stub — to be wired up to FraudDetectionAgent."""
    logger.info(f"[STUB] FraudDetection for user {user_id}")
# apps/audit/tasks.py
# FIX 3: Audit Log Archiving
# FIX 5: Daily Fraud Scan
#
# BUG FIXED IN THIS VERSION:
#   run_daily_fraud_scan previously called service.score_user() and then
#   accessed the result as result["risk_score"] and result["signals"].
#   FraudSignalService.score_user() returns a FraudResult *dataclass*,
#   not a dict. Subscript access on a dataclass raises TypeError at runtime,
#   which would silently kill the nightly fraud scan — Celery would log the
#   error and move on, meaning no user would ever be flagged automatically.
#
#   Fixed to use attribute access: result.risk_score, result.signals,
#   result.auto_action — matching the FraudResult dataclass definition.
#
#   Also fixed: auto-reject logic now uses result.auto_action == "AUTO_REJECT"
#   (the field already computed by FraudSignalService) rather than duplicating
#   the threshold check (>= 80) here. Single source of truth.

import json
import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)

ARCHIVE_AFTER_DAYS = 90
BATCH_SIZE         = 10_000


@shared_task(queue="default", max_retries=3, default_retry_delay=300)
def archive_old_audit_events():
    """
    Archive AuditEvent records older than 90 days to S3, then delete from DB.
    Runs in batches of 10,000 to keep memory usage flat.
    Scheduled: 02:00 EAT nightly via Celery beat.
    """
    from apps.audit.models import AuditEvent

    cutoff         = timezone.now() - timedelta(days=ARCHIVE_AFTER_DAYS)
    total_archived = 0
    total_deleted  = 0

    while True:
        batch = list(
            AuditEvent.objects.filter(created_at__lt=cutoff)
            .order_by("created_at")
            .values()[:BATCH_SIZE]
        )
        if not batch:
            break

        date_str   = timezone.now().strftime("%Y/%m/%d")
        batch_json = "\n".join(json.dumps(record, default=str) for record in batch)
        s3_key     = (
            f"audit-archive/{date_str}/"
            f"batch_{batch[0]['created_at'].strftime('%H%M%S')}.jsonl"
        )

        try:
            _upload_to_s3(s3_key, batch_json)
            total_archived += len(batch)
        except Exception as e:
            logger.error(f"Archive upload failed for {s3_key}: {e}")
            break  # Don't delete what we couldn't archive

        # Use raw delete to bypass the immutability guard in AuditEvent.save()
        ids           = [r["id"] for r in batch]
        deleted_count = AuditEvent.objects.filter(id__in=ids).delete()[0]
        total_deleted += deleted_count
        logger.info(f"Archived {len(batch)} audit events to s3://{s3_key}")

    logger.info(
        f"Audit archive complete: {total_archived} archived, {total_deleted} deleted"
    )
    return {"archived": total_archived, "deleted": total_deleted}


def _upload_to_s3(key: str, content: str):
    import boto3
    from django.conf import settings

    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    s3.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=key,
        Body=content.encode("utf-8"),
        ContentType="application/x-ndjson",
        StorageClass="STANDARD_IA",
    )


@shared_task(queue="default", bind=True, max_retries=3, default_retry_delay=60)
def run_daily_fraud_scan(self):
    """
    Nightly scan of users who submitted KYC in the last 24 hours.
    Scheduled: 03:00 EAT nightly via Celery beat.

    BUG FIX: FraudSignalService.score_user() returns a FraudResult dataclass.
    Previous code accessed result["risk_score"] (dict syntax) which raises
    TypeError on a dataclass. Fixed to use result.risk_score (attribute access).

    Also uses result.auto_action instead of duplicating the >= 80 threshold.
    """
    from apps.accounts.models import KYCProfile
    from apps.accounts.services.fraud_signal_service import FraudSignalService

    cutoff     = timezone.now() - timedelta(hours=24)
    recent_kyc = KYCProfile.objects.filter(
        submitted_at__gte=cutoff
    ).select_related("user")

    service = FraudSignalService()
    checked = 0
    flagged = 0
    errors  = 0

    for kyc in recent_kyc:
        try:
            # FIX: result is a FraudResult dataclass — use attribute access
            result = service.score_user(kyc.user)
            checked += 1

            if result.risk_score >= 50:
                logger.warning(
                    f"FRAUD SIGNAL: user={kyc.user.email} "
                    f"score={result.risk_score} "
                    f"level={result.risk_level} "
                    f"signals={result.signals}"
                )

            # FIX: use result.auto_action (already computed by FraudSignalService)
            # rather than duplicating the threshold check here
            if result.auto_action == "AUTO_REJECT":
                kyc.status = "REJECTED"
                kyc.rejection_reason = (
                    f"Auto-flagged by fraud scan: {', '.join(result.signals)}"
                )
                kyc.save(update_fields=["status", "rejection_reason"])
                flagged += 1
                logger.warning(
                    f"AUTO_REJECT applied: user={kyc.user.email} "
                    f"score={result.risk_score}"
                )

            elif result.auto_action == "FLAG_FOR_REVIEW":
                # Don't auto-reject — flag for manual review in admin
                # Audit event is already created inside score_user()
                logger.info(
                    f"FLAG_FOR_REVIEW: user={kyc.user.email} "
                    f"score={result.risk_score}"
                )

        except Exception as e:
            errors += 1
            logger.exception(
                f"Fraud scan failed for user {kyc.user_id}: {e}"
            )

    logger.info(
        f"Daily fraud scan complete: "
        f"{checked} checked, {flagged} auto-rejected, {errors} errors"
    )
    return {"checked": checked, "flagged": flagged, "errors": errors}
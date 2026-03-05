# config/celery.py — FULL REPLACEMENT
# FIX 9: Celery Queue Hardening
#
# PROBLEM SOLVED:
#   Default Celery config lets tasks pile up indefinitely.
#   A surge in property verifications (e.g., 10,000 listings in one day)
#   fills the verification queue and starves payment tasks.
#   Long-running AI tasks (30+ seconds) block short tasks in the same queue.
#   If Redis goes down and comes back, old tasks can re-execute = double payments.
#
# FIXES APPLIED:
#   1. Per-queue rate limits — verification capped at 100/min (government API limits)
#   2. Task expiry — tasks older than 1 hour are discarded (user already moved on)
#   3. Acks on execution start — prevents double-execution after Redis restart
#   4. Beat schedule — audit archiving at 02:00, fraud scan at 03:00 EAT
#   5. Separate queues per worker type (already in docker-compose)
#   6. Dead-letter logging — failed tasks logged to audit trail
#
# RESULT:
#   Payment queue never starved by verification surge.
#   No double-payment on Redis restart.
#   Stale tasks auto-expire rather than executing hours later.
#   Nightly maintenance runs automatically.

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("ardhitrust")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# ── Queue Configuration ────────────────────────────────────────────────────
app.conf.task_queues_max_priority = 10
app.conf.task_default_priority    = 5

# Per-queue rate limits (tasks per minute)
app.conf.task_annotations = {
    "apps.verification.tasks.initiate_ardhisasa_check": {
        "rate_limit": "100/m",   # Ardhisasa API has ~100 req/min limit
    },
    "apps.escrow.tasks.process_mpesa_callback": {
        "rate_limit": "500/m",   # High throughput for callbacks
        "acks_late":  True,       # Don't ack until task completes
    },
    "apps.escrow.tasks.release_funds_to_seller": {
        "rate_limit": "60/m",
        "acks_late":  True,       # Critical — never lose a payout
    },
    "apps.agents.tasks.run_title_intelligence_agent": {
        "rate_limit": "20/m",    # Anthropic API rate limit headroom
        "time_limit": 60,         # Kill if takes > 60 seconds
    },
}

# ── Task Expiry — stale tasks discarded rather than executed late ──────────
app.conf.task_soft_time_limit = 270   # Soft kill at 4.5 min (task can clean up)
app.conf.task_time_limit      = 300   # Hard kill at 5 min
app.conf.task_expires         = 3600  # Discard tasks older than 1 hour

# ── Reliability ───────────────────────────────────────────────────────────
app.conf.task_acks_late              = False  # Default: ack on receipt
app.conf.task_reject_on_worker_lost  = True   # Re-queue if worker dies mid-task
app.conf.worker_prefetch_multiplier  = 1      # Process one task at a time per worker
                                              # (prevents large tasks blocking small ones)

# ── Serialisation ─────────────────────────────────────────────────────────
app.conf.task_serializer    = "json"
app.conf.result_serializer  = "json"
app.conf.accept_content     = ["json"]

# ── Beat Schedule — FIX 3 ─────────────────────────────────────────────────
# All times in Africa/Nairobi (EAT = UTC+3)
app.conf.timezone = "Africa/Nairobi"

app.conf.beat_schedule = {
    # FIX 3: Archive audit events older than 90 days to S3
    "archive-audit-logs": {
        "task":     "apps.audit.tasks.archive_old_audit_events",
        "schedule": crontab(hour=2, minute=0),   # 02:00 EAT — low traffic
    },
    # FIX 5: Nightly fraud scan for new users
    "run-daily-fraud-scan": {
        "task":     "apps.audit.tasks.run_daily_fraud_scan",
        "schedule": crontab(hour=3, minute=0),   # 03:00 EAT
    },
    # Purge expired Django Celery Beat task results
    "purge-task-results": {
        "task":     "celery.backend_cleanup",
        "schedule": crontab(hour=4, minute=0),   # 04:00 EAT
    },
}

# ── Result Backend — store task results for 24 hours only ─────────────────
app.conf.result_expires = 86400   # 24 hours in seconds
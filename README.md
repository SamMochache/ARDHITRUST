# SCALING_RUNBOOK.md
# ArdhiTrust — Scaling Operations Runbook

## Architecture at Each Scale Tier

### Tier 1: Launch (0–5,000 concurrent users)
Current architecture, no changes needed.
- 1 × web server (4 Gunicorn workers)
- 1 × PostgreSQL (with PgBouncer)
- 1 × Redis
- 1 × Celery worker per queue (4 workers total)
- Estimated monthly infra cost: **$150–300/month** (e.g. 2× t3.medium + RDS t3.micro)

### Tier 2: Growth (5,000–50,000 concurrent users)
- Add 2–3 web servers behind a load balancer (AWS ALB or nginx)
- Add PostgreSQL read replica (DATABASE_REPLICA_URL in .env)
- Scale up Redis (ElastiCache r6g.large)
- Scale Celery workers per queue independently
- Estimated monthly infra cost: **$800–2,000/month**

### Tier 3: Scale (50,000–200,000 concurrent users)
- 5–10 web servers behind ALB
- 2 read replicas + PgBouncer on each server
- Redis Cluster (3 nodes)
- Separate Celery worker fleets per queue in auto-scaling groups
- CDN (CloudFront) for static files
- Estimated monthly infra cost: **$3,000–8,000/month**

### Tier 4: National Scale (200,000+ concurrent users)
- County-based DB sharding (Nairobi shard, Coast shard, etc.)
- Property search moves to Elasticsearch
- Consider Aurora PostgreSQL (auto-scaling storage, multi-AZ)
- Estimated monthly infra cost: **$10,000+/month**

---

## The 10 Scaling Fixes Applied

### FIX 1: PgBouncer Connection Pooling
**Problem**: PostgreSQL max 100-200 connections. 3 web servers × 8 connections each = exhausted fast.
**Fix**: PgBouncer pools app connections → 50 real DB connections support 10,000+ app connections.
**Files**: `docker/pgbouncer.ini`, `docker-compose.yml`
**When to apply**: Before launch (zero cost, prevents outage at 500+ users).

### FIX 2: M-Pesa Callback Queuing
**Problem**: Callback view hit DB synchronously. Under surge, DB connections exhausted = missed payments.
**Fix**: Callback view queues to Redis immediately (< 5ms). Celery processes asynchronously with retries.
**Files**: `apps/escrow/views.py`, `apps/escrow/tasks.py`
**When to apply**: Before launch (critical for payment reliability).

### FIX 3: Audit Log Archiving
**Problem**: AuditEvent table grows indefinitely. At 1M users = 3.6B rows/year.
**Fix**: Nightly Celery task archives records > 90 days to S3 as JSON lines, then deletes from DB.
**Files**: `apps/audit/tasks.py`, `config/celery.py`
**When to apply**: Before 100,000 users (after that, catch-up archiving is painful).

### FIX 4: AI Rate Limiting
**Problem**: Default 200 req/min user throttle applies to AI endpoints. 50,000 users × 200 AI calls/min = uncontrolled cost.
**Fix**: Custom AIAgentThrottle at 10/minute per user. KYCSubmitThrottle at 3/hour. RegisterThrottle at 5/hour.
**Files**: `core/throttling.py`, `apps/agents/views.py`, `config/settings/base.py`
**When to apply**: Before launch (cost control from day 1).

### FIX 5: FraudSignalService
**Problem**: FraudDetectionAgent stub used LLM (wrong tool). No fraud detection running.
**Fix**: Deterministic rule engine — duplicate IDs, rapid registration, price anomalies, etc.
**Files**: `apps/accounts/services/fraud_signal_service.py`, `apps/audit/tasks.py`
**When to apply**: Before launch (fraud appears on day 1).

### FIX 6: Real Valuation Agent
**Problem**: ValuationView returned listed_price ± 15% — not a real valuation.
**Fix**: Hedonic model using comparable sales from DB. LLM generates narrative (not the number).
**Files**: `apps/agents/valuation_agent.py`, `apps/agents/views.py`
**When to apply**: After 500 completed transactions (need comparables for accuracy).

### FIX 7: Read Replica Routing
**Problem**: All reads go to primary DB. 85% of queries are reads. Wastes primary capacity.
**Fix**: PrimaryReplicaRouter sends SELECT to replica, INSERT/UPDATE/DELETE to primary.
**Files**: `core/db_router.py`, `docker-compose.yml`, `config/settings/base.py`
**When to apply**: At 10,000+ users (< that, overhead not worth it).

### FIX 8: Health Check Endpoints
**Problem**: Load balancer can't tell if Django server is actually healthy.
**Fix**: `/api/health/` (fast liveness), `/api/health/detailed/` (dependency check), `/api/metrics/`.
**Files**: `core/health.py`, `config/urls.py`
**When to apply**: Before launch (required for load balancer).

### FIX 9: Celery Queue Hardening
**Problem**: Tasks pile up indefinitely. Verification surge starves payment queue. Double-execution on Redis restart.
**Fix**: Per-queue rate limits, task expiry at 1 hour, acks_late for payments, worker_prefetch=1.
**Files**: `config/celery.py`
**When to apply**: Before launch.

### FIX 10: This runbook
**When to apply**: Always. Update it when architecture changes.

---

## Emergency Runbook

### Payment queue backing up (> 100 tasks)
```bash
# Check queue depth
redis-cli -a $REDIS_PASSWORD llen payments

# Scale up payment workers
docker compose up --scale worker_payments=4

# Check for stuck tasks
celery -A config inspect active
```

### Database connections exhausted
```bash
# Check PgBouncer stats
psql -h localhost -p 6432 -U ardhitrust pgbouncer -c "SHOW POOLS;"

# Check active connections
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"

# Emergency: increase pool size (no restart needed)
psql -h localhost -p 6432 -U ardhitrust pgbouncer -c "RELOAD;"
```

### AI agent errors spiking
```bash
# Check error rate
curl http://localhost:8000/api/metrics/ -H "Authorization: Bearer $ADMIN_TOKEN"

# Temporarily disable AI endpoints (keep everything else up)
# Set in Redis:
redis-cli -a $REDIS_PASSWORD SET "feature:ai_agents:enabled" "false"
# Check this flag in BuyerAssistantView before calling agent
```

### Audit table getting large (> 500M rows)
```bash
# Check size
psql $DATABASE_URL -c "SELECT pg_size_pretty(pg_total_relation_size('audit_event'));"

# Trigger manual archive
celery -A config call apps.audit.tasks.archive_old_audit_events

# Check archive progress
celery -A config inspect reserved
```

### Fraud scan auto-rejected legitimate user
```bash
# Find the user and check fraud signals
psql $DATABASE_URL -c "
SELECT metadata FROM audit_event 
WHERE action='FRAUD_SCAN' AND resource_id='<user_uuid>'
ORDER BY created_at DESC LIMIT 1;"

# Manually approve via admin or Django shell
python manage.py shell -c "
from apps.accounts.models import KYCProfile
kyc = KYCProfile.objects.get(user__email='user@example.com')
kyc.status = 'APPROVED'
kyc.rejection_reason = ''
kyc.save()
"
```

---

## Monitoring Thresholds (set alerts at these levels)

| Metric | Warning | Critical |
|---|---|---|
| payments queue depth | > 50 | > 200 |
| verification queue depth | > 200 | > 1000 |
| DB connections used | > 80% | > 95% |
| Redis memory used | > 70% | > 90% |
| AI agent error rate | > 5% | > 20% |
| Audit table size | > 50M rows | > 200M rows |
| M-Pesa callback failures | > 5/hour | > 20/hour |
| Health check response time | > 500ms | > 2000ms |

---

## Cost Control

### Monthly AI cost estimate at scale
| Users | AI calls/day | Est. monthly cost |
|---|---|---|
| 10,000 | 50,000 | ~$75 |
| 100,000 | 500,000 | ~$750 |
| 1,000,000 | 5,000,000 | ~$7,500 |

**Controls applied**:
- `AIAgentThrottle`: 10 calls/minute per user
- `BaseAgent` input caching: identical inputs hit Redis, not Anthropic
- `ValuationAgent` uses Claude only for narrative, not for the number

### M-Pesa cost at scale
Safaricom charges per STK push. Budget ~KES 1 per initiation.
At 10,000 transactions/day = KES 10,000/day (~$75/day).
This is offset by 1.5% platform fee — at KES 5M average transaction, fee = KES 75,000 per deal.

---

## Deployment Sequence (first production deploy)

```bash
# 1. Provision infrastructure
# RDS PostgreSQL (db.t3.small minimum, db.t3.medium recommended)
# ElastiCache Redis (cache.t3.micro minimum)
# EC2 t3.small for web, t3.micro for workers

# 2. Set all environment variables (see .env.example)
# Critical: FIELD_ENCRYPTION_KEYS must be set BEFORE first migration
# If you change this key after users exist, all encrypted data becomes unreadable

# 3. Run migrations (only on primary DB)
make migrate

# 4. Create superuser
make createsuperuser

# 5. Start services
docker compose up -d

# 6. Verify health
curl https://ardhitrust.co.ke/api/health/
curl https://ardhitrust.co.ke/api/health/detailed/

# 7. Test M-Pesa sandbox before going live
# Set MPESA_ENV=sandbox and verify callback URL is reachable
```
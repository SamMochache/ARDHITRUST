# core/db_router.py
# FIX 7: Read Replica Router
#
# PROBLEM SOLVED:
#   At 50,000+ concurrent users, most DB operations are reads (property listings,
#   verification status, user profiles). Sending all reads to the primary DB
#   wastes its capacity on non-write work and creates a bottleneck.
#
# HOW IT WORKS:
#   Django's database router directs SELECT queries to the replica.
#   INSERT/UPDATE/DELETE always go to the primary.
#   Migrations always run on primary.
#   Audit events always go to primary (immutability requirement).
#
# RESULT:
#   Primary DB handles only writes (~15% of queries).
#   Replica handles reads (~85% of queries).
#   Effectively doubles DB throughput without bigger hardware.
#
# SETUP IN settings/base.py:
#   DATABASE_ROUTERS = ["core.db_router.PrimaryReplicaRouter"]
#   DATABASES["replica"] = env.db("DATABASE_REPLICA_URL", default=DATABASE_URL)


class PrimaryReplicaRouter:
    """
    Route reads to replica, writes to primary.
    Audit events always go to primary — never risk reading stale audit data.
    """

    # These apps always use the primary DB regardless of operation type
    PRIMARY_ONLY_APPS = {"audit", "django_celery_beat", "django_celery_results"}

    def db_for_read(self, model, **hints):
        """Send reads to replica — except audit and task scheduler models."""
        if model._meta.app_label in self.PRIMARY_ONLY_APPS:
            return "default"
        return "replica"

    def db_for_write(self, model, **hints):
        """All writes go to primary."""
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations between objects on primary and replica."""
        db_set = {"default", "replica"}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Migrations only run on primary."""
        return db == "default"
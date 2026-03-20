# apps/escrow/state_machine.py
#
# FIX: Replaced `transitions` library with a custom state machine.
#
# PROBLEMS SOLVED:
#   1. External library dependency for ~20 lines of logic we can own entirely.
#   2. MachineError was a library-specific exception — views and tests were
#      coupled to an external import for a domain concept we control.
#   3. The transitions library uses reflection magic that makes debugging hard.
#   4. Impossible to add per-transition guards (e.g. "only dispute if funded")
#      without fighting the library's abstractions.
#
# DESIGN:
#   TRANSITION_MAP is the single source of truth.
#   Each key is a trigger name. Each value is a list of (source, destination)
#   pairs — one trigger can have multiple valid source states (e.g. "dispute").
#   EscrowStateMachine.trigger(name) looks up the map, validates the current
#   state, updates it, persists to DB, and fires the after-state-change hook.
#
# MIGRATION FROM transitions LIBRARY:
#   - Replace `from transitions import MachineError` with
#     `from apps.escrow.state_machine import InvalidTransitionError`
#   - All trigger method calls (e.g. machine.fund()) work identically.
#   - Tests that caught MachineError should now catch InvalidTransitionError.
#
# EXTENDING WITH GUARDS:
#   Add a guards dict keyed by trigger name. Each guard is a callable that
#   receives the transaction and raises InvalidTransitionError with a reason.
#   Example:
#       GUARDS = {
#           "fund": lambda txn: _require_mpesa_id(txn),
#       }

from __future__ import annotations
from typing import NamedTuple


# ── Domain exception (replaces transitions.MachineError) ─────────────────────

class InvalidTransitionError(Exception):
    """
    Raised when a state transition is attempted from an invalid source state,
    or when a guard condition is not met.
    Replaces transitions.MachineError — catch this in views and tests.
    """
    pass


# ── Transition definition ─────────────────────────────────────────────────────

class Transition(NamedTuple):
    source: str
    dest:   str


# All valid states
STATES = [
    "INITIATED",
    "FUNDED",
    "SEARCH_CERTIFICATE",
    "SALE_AGREEMENT",
    "LAND_BOARD_APPROVAL",
    "TITLE_TRANSFER",
    "COMPLETED",
    "DISPUTED",
    "REFUNDED",
]

# Trigger name → list of valid (source, destination) pairs
# A trigger can have multiple valid sources (e.g. dispute, refund).
TRANSITION_MAP: dict[str, list[Transition]] = {
    "fund": [
        Transition("INITIATED", "FUNDED"),
    ],
    "start_search": [
        Transition("FUNDED", "SEARCH_CERTIFICATE"),
    ],
    "sign_agreement": [
        Transition("SEARCH_CERTIFICATE", "SALE_AGREEMENT"),
    ],
    "board_approval": [
        Transition("SALE_AGREEMENT", "LAND_BOARD_APPROVAL"),
    ],
    "transfer_title": [
        Transition("LAND_BOARD_APPROVAL", "TITLE_TRANSFER"),
    ],
    "complete": [
        Transition("TITLE_TRANSFER", "COMPLETED"),
    ],
    "dispute": [
        Transition("FUNDED",             "DISPUTED"),
        Transition("SEARCH_CERTIFICATE", "DISPUTED"),
        Transition("SALE_AGREEMENT",     "DISPUTED"),
    ],
    "refund": [
        Transition("DISPUTED",  "REFUNDED"),
        Transition("INITIATED", "REFUNDED"),
    ],
}

# Build a fast lookup: (trigger, source) → dest
_LOOKUP: dict[tuple[str, str], str] = {
    (trigger, t.source): t.dest
    for trigger, transitions in TRANSITION_MAP.items()
    for t in transitions
}

# Valid source states per trigger (used in error messages)
_VALID_SOURCES: dict[str, list[str]] = {
    trigger: [t.source for t in transitions]
    for trigger, transitions in TRANSITION_MAP.items()
}


# ── State machine ─────────────────────────────────────────────────────────────

class EscrowStateMachine:
    """
    Controls state transitions for an EscrowTransaction.

    Usage:
        machine = EscrowStateMachine(transaction)
        machine.fund()           # triggers the "fund" transition
        machine.dispute()        # triggers the "dispute" transition
        machine.trigger("fund")  # equivalent — trigger by name

    Raises:
        InvalidTransitionError — if the current state has no valid transition
        for the requested trigger, or if a guard condition fails.
    """

    def __init__(self, transaction):
        self.transaction = transaction

    @property
    def state(self) -> str:
        return self.transaction.status

    # ── Core trigger mechanism ────────────────────────────────────────────────

    def trigger(self, name: str) -> str:
        """
        Fire a named transition. Returns the new state.
        Raises InvalidTransitionError if the transition is not valid from
        the current state.
        """
        if name not in TRANSITION_MAP:
            raise InvalidTransitionError(
                f"Unknown trigger '{name}'. "
                f"Valid triggers: {sorted(TRANSITION_MAP.keys())}"
            )

        dest = _LOOKUP.get((name, self.state))
        if dest is None:
            valid = _VALID_SOURCES[name]
            raise InvalidTransitionError(
                f"Cannot trigger '{name}' from state '{self.state}'. "
                f"Valid source states for '{name}': {valid}"
            )

        # Run optional guard before committing
        self._run_guard(name)

        # Commit the transition
        self._transition_to(dest)
        return dest

    # ── Named trigger methods (mirrors transitions library API) ───────────────
    # These exist so call sites don't change: machine.fund() still works.

    def fund(self)            -> str: return self.trigger("fund")
    def start_search(self)    -> str: return self.trigger("start_search")
    def sign_agreement(self)  -> str: return self.trigger("sign_agreement")
    def board_approval(self)  -> str: return self.trigger("board_approval")
    def transfer_title(self)  -> str: return self.trigger("transfer_title")
    def complete(self)        -> str: return self.trigger("complete")
    def dispute(self)         -> str: return self.trigger("dispute")
    def refund(self)          -> str: return self.trigger("refund")

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _transition_to(self, new_state: str) -> None:
        """Persist the new state and fire the after-state-change hook."""
        self.transaction.status = new_state
        self.transaction.save(update_fields=["status", "updated_at"])
        self._after_state_change(new_state)

    def _after_state_change(self, new_state: str) -> None:
        """
        Hook fired after every successful transition.
        Mirrors the transitions library's after_state_change callback.
        """
        from apps.audit.models import AuditEvent
        AuditEvent.log(
            actor=None,
            action=f"ESCROW_{new_state}",
            resource_type="EscrowTransaction",
            resource_id=str(self.transaction.id),
        )

        from apps.notifications.tasks import send_escrow_step_notification
        send_escrow_step_notification.delay(
            str(self.transaction.buyer.id),
            str(self.transaction.seller.id),
            new_state,
        )

        if new_state == "COMPLETED":
            from apps.escrow.tasks import release_funds_to_seller
            release_funds_to_seller.delay(str(self.transaction.id))

    def _run_guard(self, trigger: str) -> None:
        """
        Optional per-trigger guard conditions.
        Extend GUARDS below to add validation without changing trigger logic.
        Raises InvalidTransitionError if a guard fails.
        """
        guard = GUARDS.get(trigger)
        if guard:
            guard(self.transaction)


# ── Guards (add per-transition validation here) ───────────────────────────────
# Each guard is a callable(transaction) that raises InvalidTransitionError
# with a clear message if the precondition is not met.

def _require_mpesa_checkout_id(txn) -> None:
    """fund() requires a valid M-Pesa checkout request ID."""
    if not txn.mpesa_checkout_request_id:
        raise InvalidTransitionError(
            "Cannot fund escrow: no M-Pesa checkout request ID recorded. "
            "Ensure the STK push was initiated before confirming payment."
        )


GUARDS: dict[str, callable] = {
    "fund": _require_mpesa_checkout_id,
}

from transitions import Machine
from apps.audit.models import AuditEvent

STATES = [
    "INITIATED", "FUNDED", "SEARCH_CERTIFICATE",
    "SALE_AGREEMENT", "LAND_BOARD_APPROVAL",
    "TITLE_TRANSFER", "COMPLETED", "DISPUTED", "REFUNDED",
]

TRANSITIONS = [
    {"trigger": "fund",           "source": "INITIATED",          "dest": "FUNDED"},
    {"trigger": "start_search",   "source": "FUNDED",             "dest": "SEARCH_CERTIFICATE"},
    {"trigger": "sign_agreement", "source": "SEARCH_CERTIFICATE", "dest": "SALE_AGREEMENT"},
    {"trigger": "board_approval", "source": "SALE_AGREEMENT",     "dest": "LAND_BOARD_APPROVAL"},
    {"trigger": "transfer_title", "source": "LAND_BOARD_APPROVAL","dest": "TITLE_TRANSFER"},
    {"trigger": "complete",       "source": "TITLE_TRANSFER",     "dest": "COMPLETED"},
    {"trigger": "dispute",        "source": ["FUNDED","SEARCH_CERTIFICATE","SALE_AGREEMENT"],
                                  "dest": "DISPUTED"},
    {"trigger": "refund",         "source": ["DISPUTED","INITIATED"], "dest": "REFUNDED"},
]

class EscrowStateMachine:
    def __init__(self, transaction):
        self.transaction = transaction
        self.machine = Machine(
            model=self, states=STATES, transitions=TRANSITIONS,
            initial=transaction.status,
            after_state_change="on_state_change",
        )

    def on_state_change(self):
        self.transaction.status = self.state
        self.transaction.save(update_fields=["status", "updated_at"])

        AuditEvent.log(
            actor=None,
            action=f"ESCROW_{self.state}",
            resource_type="EscrowTransaction",
            resource_id=str(self.transaction.id),
        )

        from apps.notifications.tasks import send_escrow_step_notification
        send_escrow_step_notification.delay(
            str(self.transaction.buyer.id),
            str(self.transaction.seller.id),
            self.state,
        )

        if self.state == "COMPLETED":
            from apps.escrow.tasks import release_funds_to_seller
            release_funds_to_seller.delay(str(self.transaction.id))
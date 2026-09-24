"""Ticket domain model."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class SAPModule(str, Enum):
    MM = "MM"
    UNKNOWN = "UNKNOWN"


class TicketIntent(str, Enum):
    TROUBLESHOOTING = "Troubleshooting"
    STATUS_CHECK = "Status Check"
    HOW_TO = "How-To"
    GENERAL_SUPPORT = "General Support"


@dataclass
class Ticket:
    description: str
    ticket_id: str = field(default_factory=lambda: str(uuid4()))
    sap_module: SAPModule = SAPModule.MM
    process: str | None = None
    intent: TicketIntent = TicketIntent.GENERAL_SUPPORT
    document_number: str | None = None
    transaction_code: str | None = None
    error_message: str | None = None
    requested_action: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        self.description = self.description.strip()
        if not self.description:
            raise ValueError("Ticket description cannot be empty.")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["sap_module"] = self.sap_module.value
        data["intent"] = self.intent.value
        return data

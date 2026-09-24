"""Read-only simulated SAP interface for the POC.

The contract intentionally resembles a real integration boundary. The mock can
later be replaced by an OData/API implementation without changing assistant
business logic.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SAPObjectNotFoundError(LookupError):
    pass


class SAPMockClient:
    def __init__(self, data_path: str | Path = "mock_data") -> None:
        self.data_path = Path(data_path)

    def _load(self, filename: str) -> list[dict[str, Any]]:
        path = self.data_path / filename
        if not path.exists():
            return []

        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            return payload.get("items", [])
        return []

    @staticmethod
    def _find(
        items: list[dict[str, Any]],
        value: str,
        candidate_keys: tuple[str, ...],
    ) -> dict[str, Any]:
        expected = str(value)
        for item in items:
            if any(str(item.get(key, "")) == expected for key in candidate_keys):
                return item
        raise SAPObjectNotFoundError(f"SAP mock object '{value}' was not found.")

    def get_purchase_order(self, po_number: str) -> dict[str, Any]:
        return self._find(
            self._load("purchase_orders.json"),
            po_number,
            ("po_number", "purchase_order", "id"),
        )

    def get_purchase_requisition(self, pr_number: str) -> dict[str, Any]:
        return self._find(
            self._load("purchase_requisitions.json"),
            pr_number,
            ("pr_number", "purchase_requisition", "id"),
        )

    def get_goods_receipt(self, document_number: str) -> dict[str, Any]:
        return self._find(
            self._load("goods_receipts.json"),
            document_number,
            ("document_number", "material_document", "id"),
        )

    def get_invoice(self, invoice_number: str) -> dict[str, Any]:
        return self._find(
            self._load("invoices.json"),
            invoice_number,
            ("invoice_number", "document_number", "id"),
        )

    def get_vendor(self, vendor_id: str) -> dict[str, Any]:
        return self._find(
            self._load("vendors.json"),
            vendor_id,
            ("vendor_id", "supplier_id", "id"),
        )

    def get_release_status(self, po_number: str) -> dict[str, Any]:
        po = self.get_purchase_order(po_number)
        return {
            "po_number": po_number,
            "release_status": po.get("release_status", "UNKNOWN"),
            "release_strategy": po.get("release_strategy"),
            "released_by": po.get("released_by"),
        }

    # No mutation methods are exposed in the POC. Posting, releasing, changing
    # configuration or modifying master data remains a human-controlled action.

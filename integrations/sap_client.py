"""Read-only SAP integration boundary.

This adapter deliberately exposes only read operations. A production evolution
could replace the mock with authenticated SAP OData/API calls while retaining
the same interface and authorization boundary.
"""

from __future__ import annotations

from typing import Any, Protocol

from app.config import settings
from app.sap_mock import SAPMockClient, SAPObjectNotFoundError


class SAPIntegrationError(RuntimeError):
    pass


class SAPReadOnlyError(PermissionError):
    pass


class SAPReadProvider(Protocol):
    def get_purchase_order(self, po_number: str) -> dict[str, Any]: ...
    def get_purchase_requisition(self, pr_number: str) -> dict[str, Any]: ...
    def get_goods_receipt(self, document_number: str) -> dict[str, Any]: ...
    def get_invoice(self, invoice_number: str) -> dict[str, Any]: ...
    def get_vendor(self, vendor_id: str) -> dict[str, Any]: ...
    def get_release_status(self, po_number: str) -> dict[str, Any]: ...


class SAPClient:
    """Stable read-only contract used by the assistant."""

    def __init__(self, provider: SAPReadProvider | None = None) -> None:
        if provider is not None:
            self.provider = provider
        elif settings.use_mock_sap:
            self.provider = SAPMockClient()
        else:
            raise SAPIntegrationError(
                "A real SAP provider is not configured. "
                "Set USE_MOCK_SAP=true for the POC."
            )

    def _read(self, operation: str, value: str) -> dict[str, Any]:
        try:
            method = getattr(self.provider, operation)
            return method(value)
        except SAPObjectNotFoundError:
            raise
        except Exception as exc:
            raise SAPIntegrationError(
                f"SAP read operation '{operation}' failed."
            ) from exc

    def get_purchase_order(self, po_number: str) -> dict[str, Any]:
        return self._read("get_purchase_order", po_number)

    def get_purchase_requisition(self, pr_number: str) -> dict[str, Any]:
        return self._read("get_purchase_requisition", pr_number)

    def get_goods_receipt(self, document_number: str) -> dict[str, Any]:
        return self._read("get_goods_receipt", document_number)

    def get_invoice(self, invoice_number: str) -> dict[str, Any]:
        return self._read("get_invoice", invoice_number)

    def get_vendor(self, vendor_id: str) -> dict[str, Any]:
        return self._read("get_vendor", vendor_id)

    def get_release_status(self, po_number: str) -> dict[str, Any]:
        return self._read("get_release_status", po_number)

    # Explicitly deny state-changing operations in this POC.
    def release_purchase_order(self, *_: Any, **__: Any) -> None:
        raise SAPReadOnlyError(
            "Purchase-order release requires authorized human execution."
        )

    def post_goods_receipt(self, *_: Any, **__: Any) -> None:
        raise SAPReadOnlyError(
            "Goods-receipt posting requires authorized human execution."
        )

    def post_invoice(self, *_: Any, **__: Any) -> None:
        raise SAPReadOnlyError(
            "Invoice posting requires authorized human execution."
        )

    def change_configuration(self, *_: Any, **__: Any) -> None:
        raise SAPReadOnlyError(
            "SAP configuration changes are outside AI autonomy."
        )

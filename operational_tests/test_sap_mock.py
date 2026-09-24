from pathlib import Path

import pytest

from app.sap_mock import SAPMockClient, SAPObjectNotFoundError


REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def sap():
    return SAPMockClient(REPO_ROOT / "mock_data")


def test_reads_purchase_order(sap):
    po = sap.get_purchase_order("4500012345")
    assert po["po_number"] == "4500012345"
    assert po["release_status"] == "PENDING"


def test_reads_invoice(sap):
    invoice = sap.get_invoice("5100002002")
    assert invoice["blocked"] is True
    assert invoice["invoice_unit_price"] == 620.00


def test_reads_release_status(sap):
    status = sap.get_release_status("4500012345")
    assert status is not None


def test_unknown_object_raises(sap):
    with pytest.raises(SAPObjectNotFoundError):
        sap.get_purchase_order("4500099999")


def test_mock_client_exposes_no_mutation_api(sap):
    prohibited = [
        "release_purchase_order",
        "post_goods_receipt",
        "post_invoice",
        "change_configuration",
    ]
    for method in prohibited:
        assert not hasattr(sap, method)

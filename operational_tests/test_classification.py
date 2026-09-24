from app.classification import classify_ticket


def test_classifies_purchase_order_release():
    result = classify_ticket(
        "PO 4500012345 is blocked and is still pending release approval."
    )
    assert result.module == "MM"
    assert result.process == "Release Strategy"
    assert result.intent in {"Troubleshooting", "Status Check", "How-To"}


def test_classifies_invoice_verification():
    result = classify_ticket(
        "Invoice 5100002002 is blocked in MIRO and the invoice price differs from the PO."
    )
    assert result.module == "MM"
    assert result.process == "Invoice Verification"


def test_unknown_process_requests_clarification():
    result = classify_ticket("SAP is not working as expected.")
    assert result.process == "Unknown"
    assert result.requires_clarification is True

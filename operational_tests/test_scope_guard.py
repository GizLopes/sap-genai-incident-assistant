from app.scope_guard import check_scope


def test_mm_purchase_order_is_in_scope():
    result = check_scope("PO 4500012345 is blocked for release.")
    assert result.in_scope is True


def test_sd_sales_order_is_out_of_scope():
    result = check_scope(
        "SAP SD sales order 7000012345 is blocked for delivery."
    )
    assert result.in_scope is False


def test_hcm_request_is_out_of_scope():
    result = check_scope(
        "SAP HCM employee payroll data is incorrect."
    )
    assert result.in_scope is False

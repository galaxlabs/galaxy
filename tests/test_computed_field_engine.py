from galaxy.core.doctype.computed_field_engine import (
    evaluate_computed_field,
    evaluate_computed_fields,
    evaluate_and_apply_computed_fields,
)
from galaxy.core.doctype.runtimemeta import merge_meta


DT = {"name": "Invoice", "module": "Accounting", "app_name": "erp",
      "table_name": "tabInvoice", "is_single": False, "is_submittable": True,
      "is_child_table": False, "is_tree": False, "idx": 0, "migration_status": "applied"}
FIELDS = [
    {"fieldname": "amount", "label": "Amount", "fieldtype": "Float", "reqd": True, "hidden": False, "read_only": False, "in_list_view": True, "idx": 0},
    {"fieldname": "qty", "label": "Qty", "fieldtype": "Int", "reqd": True, "hidden": False, "read_only": False, "in_list_view": True, "idx": 1},
    {"fieldname": "discount", "label": "Discount", "fieldtype": "Float", "reqd": False, "hidden": False, "read_only": False, "in_list_view": False, "idx": 2},
    {"fieldname": "total", "label": "Total", "fieldtype": "Float", "reqd": False, "hidden": False, "read_only": True, "in_list_view": True, "idx": 3},
]
PERMS = [{"role": "System Manager", "permlevel": 0, "read": True, "write": True, "create": True, "delete": True, "idx": 0}]


def test_evaluate_computed_field_arith():
    cf = {"field_name": "total", "formula": "amount * qty", "fieldtype": "Float", "script_type": "Expression", "enabled": True}
    result = evaluate_computed_field(cf, {"amount": 100, "qty": 3})
    assert result == 300


def test_evaluate_computed_field_with_discount():
    cf = {"field_name": "total", "formula": "(amount * qty) - discount", "fieldtype": "Float", "script_type": "Expression", "enabled": True}
    result = evaluate_computed_field(cf, {"amount": 100, "qty": 3, "discount": 50})
    assert result == 250


def test_evaluate_computed_field_str():
    cf = {"field_name": "label", "formula": "'Order-' + str(code)", "fieldtype": "Data", "script_type": "Expression", "enabled": True}
    result = evaluate_computed_field(cf, {"code": "ABC"})
    assert result == "Order-ABC"


def test_evaluate_computed_field_empty_formula():
    cf = {"field_name": "total", "formula": "", "fieldtype": "Float", "script_type": "Expression", "enabled": True}
    result = evaluate_computed_field(cf, {"amount": 100})
    assert result is None


def test_evaluate_computed_fields_multiple():
    meta = merge_meta(DT, FIELDS, PERMS, computed_fields=[
        {"field_name": "total", "formula": "amount * qty", "fieldtype": "Float", "script_type": "Expression", "enabled": True, "idx": 0},
    ])
    results = evaluate_computed_fields(meta, {"amount": 50, "qty": 4})
    assert results["total"] == 200


def test_evaluate_computed_fields_disabled_skipped():
    meta = merge_meta(DT, FIELDS, PERMS, computed_fields=[
        {"field_name": "total", "formula": "amount * qty", "fieldtype": "Float", "script_type": "Expression", "enabled": False, "idx": 0},
    ])
    results = evaluate_computed_fields(meta, {"amount": 50, "qty": 4})
    assert "total" not in results


def test_evaluate_and_apply():
    meta = merge_meta(DT, FIELDS, PERMS, computed_fields=[
        {"field_name": "total", "formula": "amount * qty", "fieldtype": "Float", "script_type": "Expression", "enabled": True, "idx": 0},
    ])
    result = evaluate_and_apply_computed_fields(meta, {"amount": 10, "qty": 5})
    assert result["total"] == 50
    assert result["amount"] == 10


def test_no_computed_fields():
    meta = merge_meta(DT, FIELDS, PERMS)
    results = evaluate_computed_fields(meta, {"amount": 100})
    assert results == {}

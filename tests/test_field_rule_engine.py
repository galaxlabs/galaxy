from galaxy.core.doctype.field_rule_engine import _safe_eval, validate_field_rules
from galaxy.core.doctype.runtimemeta import merge_meta


DT = {"name": "Invoice", "module": "Accounting", "app_name": "erp",
      "table_name": "tabInvoice", "is_single": False, "is_submittable": True,
      "is_child_table": False, "is_tree": False, "idx": 0, "migration_status": "applied"}
FIELDS = [
    {"fieldname": "amount", "label": "Amount", "fieldtype": "Float", "reqd": True, "hidden": False, "read_only": False, "in_list_view": True, "idx": 0},
    {"fieldname": "qty", "label": "Qty", "fieldtype": "Int", "reqd": False, "hidden": False, "read_only": False, "in_list_view": True, "idx": 1},
    {"fieldname": "email", "label": "Email", "fieldtype": "Data", "reqd": False, "hidden": False, "read_only": False, "in_list_view": True, "idx": 2},
    {"fieldname": "code", "label": "Code", "fieldtype": "Data", "reqd": False, "hidden": False, "read_only": False, "in_list_view": False, "idx": 3},
    {"fieldname": "status", "label": "Status", "fieldtype": "Select", "options": "Draft\nSubmitted\nCancelled", "reqd": True, "hidden": False, "read_only": False, "in_list_view": True, "idx": 4},
]
PERMS = [{"role": "System Manager", "permlevel": 0, "read": True, "write": True, "create": True, "delete": True, "idx": 0}]


def test_safe_eval_basic_arith():
    assert _safe_eval("1 + 2", {}) == 3


def test_safe_eval_comparison():
    assert _safe_eval("10 > 5", {}) is True
    assert _safe_eval("3 == 4", {}) is False


def test_safe_eval_with_context():
    assert _safe_eval("doc.amount > 100", {"doc": {"amount": 200}}) is True
    assert _safe_eval("doc.amount > 100", {"doc": {"amount": 50}}) is False


def test_safe_eval_bool_and():
    assert _safe_eval("True and False", {}) is False
    assert _safe_eval("True and True", {}) is True


def test_safe_eval_bool_or():
    assert _safe_eval("True or False", {}) is True
    assert _safe_eval("False or False", {}) is False


def test_safe_eval_whitelisted_funcs():
    assert _safe_eval("len('abc')", {}) == 3
    assert _safe_eval("abs(-5)", {}) == 5
    assert _safe_eval("round(3.7)", {}) == 4


def test_safe_eval_direct_variable():
    assert _safe_eval("amount", {"amount": 100}) == 100


def test_safe_eval_string():
    assert _safe_eval("'hello' + ' ' + 'world'", {}) == "hello world"


def test_safe_eval_in_operator():
    ctx = {"status": "Submitted"}
    assert _safe_eval("status in ('Draft', 'Submitted')", ctx) is True
    assert _safe_eval("status in ('Draft', 'Cancelled')", ctx) is False


def test_validate_min_value():
    meta = merge_meta(DT, FIELDS, PERMS, field_rules=[
        {"field_name": "amount", "rule_type": "min_value", "value": "0", "enabled": True, "idx": 0},
    ])
    errs = validate_field_rules(meta, {"amount": -5})
    assert any("at least 0" in e for e in errs)
    errs = validate_field_rules(meta, {"amount": 10})
    assert len(errs) == 0


def test_validate_max_value():
    meta = merge_meta(DT, FIELDS, PERMS, field_rules=[
        {"field_name": "qty", "rule_type": "max_value", "value": "100", "enabled": True, "idx": 0},
    ])
    errs = validate_field_rules(meta, {"qty": 200})
    assert any("at most 100" in e for e in errs)
    errs = validate_field_rules(meta, {"qty": 50})
    assert len(errs) == 0


def test_validate_required():
    meta = merge_meta(DT, FIELDS, PERMS, field_rules=[
        {"field_name": "email", "rule_type": "required", "enabled": True, "idx": 0},
    ])
    errs = validate_field_rules(meta, {"email": ""})
    assert any("required" in e.lower() for e in errs)
    errs = validate_field_rules(meta, {"email": "a@b.com"})
    assert len(errs) == 0


def test_validate_mandatory_if():
    meta = merge_meta(DT, FIELDS, PERMS, field_rules=[
        {"field_name": "code", "rule_type": "mandatory_if", "condition": "doc.amount > 1000", "enabled": True, "idx": 0},
    ])
    errs = validate_field_rules(meta, {"amount": 2000, "code": ""})
    assert any("required" in e.lower() for e in errs)
    errs = validate_field_rules(meta, {"amount": 2000, "code": "X"})
    assert len(errs) == 0
    errs = validate_field_rules(meta, {"amount": 100, "code": ""})
    assert len(errs) == 0


def test_validate_min_length():
    meta = merge_meta(DT, FIELDS, PERMS, field_rules=[
        {"field_name": "code", "rule_type": "min_length", "value": "3", "enabled": True, "idx": 0},
    ])
    errs = validate_field_rules(meta, {"code": "ab"})
    assert any("at least 3" in e for e in errs)
    errs = validate_field_rules(meta, {"code": "abcd"})
    assert len(errs) == 0


def test_validate_disabled_rule_skipped():
    meta = merge_meta(DT, FIELDS, PERMS, field_rules=[
        {"field_name": "amount", "rule_type": "min_value", "value": "0", "enabled": False, "idx": 0},
    ])
    errs = validate_field_rules(meta, {"amount": -1})
    assert len(errs) == 0


def test_no_rules_no_errors():
    meta = merge_meta(DT, FIELDS, PERMS)
    errs = validate_field_rules(meta, {"amount": -1})
    assert len(errs) == 0

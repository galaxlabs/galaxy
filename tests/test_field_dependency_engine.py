from galaxy.model.field_dependency_engine import (
    evaluate_dependency,
    get_effective_field_states,
    resolve_field_dependencies,
)
from galaxy.model.runtimemeta import merge_meta


DT = {"name": "Invoice", "module": "Accounting", "app_name": "erp",
      "table_name": "tabInvoice", "is_single": False, "is_submittable": True,
      "is_child_table": False, "is_tree": False, "idx": 0, "migration_status": "applied"}
FIELDS = [
    {"fieldname": "has_discount", "label": "Has Discount", "fieldtype": "Check", "reqd": False, "hidden": False, "read_only": False, "in_list_view": False, "idx": 0},
    {"fieldname": "discount", "label": "Discount", "fieldtype": "Float", "reqd": False, "hidden": False, "read_only": False, "in_list_view": False, "idx": 1},
    {"fieldname": "status", "label": "Status", "fieldtype": "Select", "options": "Draft\nSubmitted\nCancelled", "reqd": True, "hidden": False, "read_only": False, "in_list_view": True, "idx": 2},
    {"fieldname": "notes", "label": "Notes", "fieldtype": "Text", "reqd": False, "hidden": False, "read_only": False, "in_list_view": False, "idx": 3},
]
PERMS = [{"role": "System Manager", "permlevel": 0, "read": True, "write": True, "create": True, "delete": True, "idx": 0}]


def test_evaluate_dependency_eq_true():
    dep = {"field_name": "discount", "depends_on_field": "has_discount", "depends_on_value": "1", "operator": "=", "action": "show", "enabled": True}
    assert evaluate_dependency(dep, {"has_discount": 1}) is True
    assert evaluate_dependency(dep, {"has_discount": 0}) is False


def test_evaluate_dependency_is_set():
    dep = {"field_name": "notes", "depends_on_field": "status", "operator": "is_set", "action": "require", "enabled": True}
    assert evaluate_dependency(dep, {"status": "Submitted"}) is True
    assert evaluate_dependency(dep, {"status": ""}) is False


def test_evaluate_dependency_is_not_set():
    dep = {"field_name": "notes", "depends_on_field": "status", "operator": "is_not_set", "action": "hide", "enabled": True}
    assert evaluate_dependency(dep, {"status": ""}) is True
    assert evaluate_dependency(dep, {"status": "Draft"}) is False


def test_evaluate_dependency_gt():
    dep = {"field_name": "discount", "depends_on_field": "amount", "operator": ">", "depends_on_value": "1000", "action": "show", "enabled": True}
    assert evaluate_dependency(dep, {"amount": 1500}) is True
    assert evaluate_dependency(dep, {"amount": 500}) is False


def test_evaluate_dependency_in():
    dep = {"field_name": "notes", "depends_on_field": "status", "operator": "in", "depends_on_value": "Submitted\nCancelled", "action": "require", "enabled": True}
    assert evaluate_dependency(dep, {"status": "Submitted"}) is True
    assert evaluate_dependency(dep, {"status": "Draft"}) is False


def test_disabled_dependency_returns_false():
    dep = {"field_name": "discount", "depends_on_field": "has_discount", "depends_on_value": "1", "operator": "=", "action": "show", "enabled": False}
    assert evaluate_dependency(dep, {"has_discount": 1}) is False


def test_resolve_hide_field():
    meta = merge_meta(DT, FIELDS, PERMS, field_dependencies=[
        {"field_name": "discount", "depends_on_field": "has_discount", "depends_on_value": "1", "action": "show", "enabled": True, "idx": 0},
    ])
    deps = resolve_field_dependencies(meta, {"has_discount": 0})
    assert "discount" in deps
    assert deps["discount"][0]["action"] == "show"
    assert deps["discount"][0]["effective"] is False


def test_resolve_require_field():
    meta = merge_meta(DT, FIELDS, PERMS, field_dependencies=[
        {"field_name": "notes", "depends_on_field": "status", "depends_on_value": "Submitted", "action": "require", "enabled": True, "idx": 0},
    ])
    deps = resolve_field_dependencies(meta, {"status": "Submitted"})
    assert deps["notes"][0]["action"] == "require"
    assert deps["notes"][0]["effective"] is True


def test_get_effective_field_states_hide():
    meta = merge_meta(DT, FIELDS, PERMS, field_dependencies=[
        {"field_name": "discount", "depends_on_field": "has_discount", "depends_on_value": "1", "action": "show", "enabled": True, "idx": 0},
    ])
    states = get_effective_field_states(meta, {"has_discount": 0})
    assert states["discount"]["hidden"] is True


def test_get_effective_field_states_no_deps():
    meta = merge_meta(DT, FIELDS, PERMS)
    states = get_effective_field_states(meta, {})
    assert states["discount"]["hidden"] is False
    assert states["discount"]["required"] is False

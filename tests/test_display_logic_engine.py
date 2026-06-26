from galaxy.model.display_logic_engine import get_effective_visibility, resolve_display_logic
from galaxy.model.runtimemeta import RuntimeMeta


def _meta(display_logic: list[dict] | None = None) -> RuntimeMeta:
    return RuntimeMeta(
        doctype={"name": "Invoice", "migration_status": "applied"},
        fields=[
            {"fieldname": "amount", "label": "Amount", "fieldtype": "Float", "reqd": True, "hidden": False, "read_only": False},
            {"fieldname": "status", "label": "Status", "fieldtype": "Select", "reqd": True, "hidden": False, "read_only": False},
            {"fieldname": "discount", "label": "Discount", "fieldtype": "Float", "reqd": False, "hidden": True, "read_only": False},
            {"fieldname": "notes", "label": "Notes", "fieldtype": "Text", "reqd": False, "hidden": False, "read_only": True},
        ],
        permissions=[],
        display_logic=display_logic or [],
        display_logic_map={},
    )


def test_resolve_empty():
    meta = _meta()
    result = resolve_display_logic(meta, {})
    assert result == {}


def test_resolve_disabled_excluded():
    meta = _meta([
        {"field_name": "discount", "depends_on_field": "status", "operator": "=", "value": "Submitted", "action": "show", "enabled": False, "idx": 0},
    ])
    result = resolve_display_logic(meta, {"status": "Submitted"})
    assert result == {}


def test_resolve_eq_show():
    meta = _meta([
        {"field_name": "discount", "depends_on_field": "status", "operator": "=", "value": "Submitted", "action": "show", "enabled": True, "idx": 0},
    ])
    result = resolve_display_logic(meta, {"status": "Submitted"})
    assert "discount" in result
    assert result["discount"][0]["action"] == "show"
    assert result["discount"][0]["effective"] is True


def test_resolve_eq_show_not_matching():
    meta = _meta([
        {"field_name": "discount", "depends_on_field": "status", "operator": "=", "value": "Submitted", "action": "show", "enabled": True, "idx": 0},
    ])
    result = resolve_display_logic(meta, {"status": "Draft"})
    assert "discount" in result
    assert result["discount"][0]["effective"] is False


def test_resolve_hide():
    meta = _meta([
        {"field_name": "discount", "depends_on_field": "status", "operator": "=", "value": "Cancelled", "action": "hide", "enabled": True, "idx": 0},
    ])
    result = resolve_display_logic(meta, {"status": "Cancelled"})
    assert result["discount"][0]["action"] == "hide"
    assert result["discount"][0]["effective"] is True


def test_visibility_defaults():
    meta = _meta()
    states = get_effective_visibility(meta, {})
    assert states["amount"]["hidden"] is False
    assert states["amount"]["required"] is True
    assert states["discount"]["hidden"] is True
    assert states["notes"]["read_only"] is True


def test_visibility_show_reveals_hidden_field():
    meta = _meta([
        {"field_name": "discount", "depends_on_field": "status", "operator": "=", "value": "Submitted", "action": "show", "enabled": True, "idx": 0},
    ])
    states = get_effective_visibility(meta, {"status": "Submitted"})
    assert states["discount"]["hidden"] is False


def test_visibility_show_not_matching_keeps_hidden():
    meta = _meta([
        {"field_name": "discount", "depends_on_field": "status", "operator": "=", "value": "Submitted", "action": "show", "enabled": True, "idx": 0},
    ])
    states = get_effective_visibility(meta, {"status": "Draft"})
    assert states["discount"]["hidden"] is True


def test_visibility_hide_hides_field():
    meta = _meta([
        {"field_name": "amount", "depends_on_field": "status", "operator": "=", "value": "Cancelled", "action": "hide", "enabled": True, "idx": 0},
    ])
    states = get_effective_visibility(meta, {"status": "Cancelled"})
    assert states["amount"]["hidden"] is True


def test_visibility_require():
    meta = _meta([
        {"field_name": "notes", "depends_on_field": "status", "operator": "=", "value": "Submitted", "action": "require", "enabled": True, "idx": 0},
    ])
    states = get_effective_visibility(meta, {"status": "Submitted"})
    assert states["notes"]["required"] is True


def test_visibility_readonly():
    meta = _meta([
        {"field_name": "amount", "depends_on_field": "status", "operator": "=", "value": "Approved", "action": "readonly", "enabled": True, "idx": 0},
    ])
    states = get_effective_visibility(meta, {"status": "Approved"})
    assert states["amount"]["read_only"] is True


def test_visibility_multiple_rules_same_field():
    meta = _meta([
        {"field_name": "discount", "depends_on_field": "status", "operator": "=", "value": "Submitted", "action": "show", "enabled": True, "idx": 0},
        {"field_name": "discount", "depends_on_field": "status", "operator": "=", "value": "Cancelled", "action": "hide", "enabled": True, "idx": 1},
    ])
    states = get_effective_visibility(meta, {"status": "Submitted"})
    assert states["discount"]["hidden"] is False
    states = get_effective_visibility(meta, {"status": "Cancelled"})
    assert states["discount"]["hidden"] is True


def test_visibility_inequality():
    meta = _meta([
        {"field_name": "discount", "depends_on_field": "amount", "operator": ">", "value": "1000", "action": "require", "enabled": True, "idx": 0},
    ])
    states = get_effective_visibility(meta, {"amount": 2000})
    assert states["discount"]["required"] is True
    states = get_effective_visibility(meta, {"amount": 500})
    assert states["discount"]["required"] is False


def test_resolve_not_missing_depends_on():
    meta = _meta([
        {"field_name": "discount", "depends_on_field": "", "operator": "=", "value": "", "action": "show", "enabled": True, "idx": 0},
    ])
    result = resolve_display_logic(meta, {})
    assert result == {}

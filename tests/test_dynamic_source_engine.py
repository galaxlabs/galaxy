from galaxy.model.dynamic_source_engine import (
    _check_dependencies,
    _resolve_source,
    _resolve_static,
    resolve_all_field_options,
    resolve_field_options,
)
from galaxy.model.runtimemeta import RuntimeMeta


def _meta(sources: dict[str, list] | None = None) -> RuntimeMeta:
    return RuntimeMeta(
        doctype={"name": "Invoice", "migration_status": "applied"},
        fields=[
            {"fieldname": "name", "fieldtype": "Data", "label": "Name"},
            {"fieldname": "customer", "fieldtype": "Data", "label": "Customer"},
            {"fieldname": "status", "fieldtype": "Select", "options": "Draft\nSubmitted\nCancelled", "label": "Status"},
            {"fieldname": "items", "fieldtype": "Table", "label": "Items"},
        ],
        permissions=[],
        dynamic_sources=sources or {},
    )


def test_resolve_empty():
    meta = _meta()
    result = resolve_field_options(meta, "customer", {})
    assert result == []


def test_resolve_all_empty():
    meta = _meta()
    result = resolve_all_field_options(meta, {})
    assert result == {}


def test_resolve_static_basic():
    meta = _meta({"customer": [{"field_name": "customer", "source_type": "static", "source_handler": "Acme\nBeta\nGamma", "enabled": True}]})
    result = resolve_field_options(meta, "customer", {})
    assert len(result) == 3
    assert result[0] == {"value": "Acme", "label": "Acme"}


def test_resolve_static_single():
    result = _resolve_static("OnlyOption")
    assert len(result) == 1
    assert result[0]["value"] == "OnlyOption"


def test_resolve_static_empty():
    assert _resolve_static("") == []
    assert _resolve_static("  ") == []


def test_resolve_disabled_excluded():
    meta = _meta({"customer": [{"field_name": "customer", "source_type": "static", "source_handler": "X", "enabled": False}]})
    result = resolve_field_options(meta, "customer", {})
    assert result == []


def test_resolve_permission_required():
    meta = _meta({"customer": [{"field_name": "customer", "source_type": "static", "source_handler": "Secret\nData", "enabled": True, "permission_required": "Admin"}]})
    result = resolve_field_options(meta, "customer", {}, role="User")
    assert result == []

    result = resolve_field_options(meta, "customer", {}, role="Admin")
    assert len(result) == 2


def test_check_dependencies_satisfied():
    assert _check_dependencies({"status": "Submitted"}, {"status": "Submitted"}) is True


def test_check_dependencies_not_satisfied():
    assert _check_dependencies({"status": "Submitted"}, {"status": "Draft"}) is False


def test_check_dependencies_list():
    assert _check_dependencies({"status": ["Draft", "Submitted"]}, {"status": "Submitted"}) is True
    assert _check_dependencies({"status": ["Draft", "Submitted"]}, {"status": "Cancelled"}) is False


def test_check_dependencies_missing_field():
    assert _check_dependencies({"status": "Submitted"}, {}) is False


def test_check_dependencies_json_string():
    assert _check_dependencies('{"status": "Submitted"}', {"status": "Submitted"}) is True


def test_check_dependencies_none():
    assert _check_dependencies(None, {}) is True


def test_check_dependencies_invalid():
    assert _check_dependencies("not-json", {"status": "X"}) is True


def test_source_resolve_unknown_type():
    result = _resolve_source({"source_type": "unknown", "source_handler": ""}, {})
    assert result == []


def test_source_resolve_static():
    result = _resolve_source({"source_type": "static", "source_handler": "A\nB"}, {})
    assert len(result) == 2


def test_resolve_all_returns_all():
    meta = _meta({
        "customer": [{"field_name": "customer", "source_type": "static", "source_handler": "Acme\nBeta", "enabled": True}],
        "status": [{"field_name": "status", "source_type": "static", "source_handler": "Open\nClosed", "enabled": True}],
    })
    result = resolve_all_field_options(meta, {})
    assert "customer" in result
    assert "status" in result
    assert len(result["customer"]) == 2
    assert len(result["status"]) == 2


def test_resolve_script_list():
    meta = _meta({"customer": [{"field_name": "customer", "source_type": "script", "source_handler": '["X", "Y", "Z"]', "enabled": True}]})
    result = resolve_field_options(meta, "customer", {})
    assert result == ["X", "Y", "Z"]


def test_resolve_script_dict():
    meta = _meta({"customer": [{"field_name": "customer", "source_type": "script", "source_handler": '{"A": "Alpha", "B": "Beta"}', "enabled": True}]})
    result = resolve_field_options(meta, "customer", {})
    assert {"value": "A", "label": "Alpha"} in result
    assert {"value": "B", "label": "Beta"} in result


def test_resolve_script_empty():
    result = _resolve_source({"source_type": "script", "source_handler": ""}, {})
    assert result == []


def test_resolve_document_no_handler():
    result = _resolve_source({"source_type": "document", "source_handler": ""}, {})
    assert result == []

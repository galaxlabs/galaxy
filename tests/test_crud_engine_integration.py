from galaxy.config import load_site_config
from galaxy.model.document import create_document, update_document, get_document
from galaxy.model.meta_cache import meta_cache
from galaxy.database.connection import get_engine
from sqlalchemy import text

DOCTYPE = "Module Def"


def _engine():
    _, site = load_site_config()
    return get_engine(site)


def _cleanup_doc(name: str):
    with _engine().begin() as conn:
        conn.execute(text('DELETE FROM "tabModule Def" WHERE name = :n'), {"n": name})


def _insert_field_rule(field_name: str, rule_type: str, value: str, condition: str = ""):
    with _engine().begin() as conn:
        conn.execute(text("""
            INSERT INTO "tabFieldRule" (name, parent, field_name, rule_type, "value", condition, enabled)
            VALUES (:name, :parent, :field_name, :rule_type, :value, :condition, TRUE)
        """), {
            "name": f"test-{field_name}-{rule_type}",
            "parent": DOCTYPE,
            "field_name": field_name,
            "rule_type": rule_type,
            "value": value,
            "condition": condition,
        })


def _insert_computed_field(field_name: str, formula: str):
    with _engine().begin() as conn:
        conn.execute(text("""
            INSERT INTO "tabComputedField" (name, parent, field_name, formula, fieldtype, script_type, enabled)
            VALUES (:name, :parent, :field_name, :formula, 'Data', 'Python', TRUE)
        """), {
            "name": f"test-cf-{field_name}",
            "parent": DOCTYPE,
            "field_name": field_name,
            "formula": formula,
        })


def _delete_test_rules():
    with _engine().begin() as conn:
        conn.execute(text("""DELETE FROM "tabFieldRule" WHERE name LIKE 'test-%'"""))
        conn.execute(text("""DELETE FROM "tabComputedField" WHERE name LIKE 'test-%'"""))


def _invalidate_cache():
    meta_cache.invalidate(DOCTYPE)


def test_create_enforces_field_rule_min_length():
    _delete_test_rules()
    try:
        _insert_field_rule("module_name", "min_length", "5")
        _invalidate_cache()

        result = create_document(DOCTYPE, {"module_name": "AB", "app_name": "core"})
        assert result["success"] is False
        assert "Field rule validation failed" in result["error"]
        assert any("at least 5" in e for e in result["errors"])
    finally:
        _delete_test_rules()
        _invalidate_cache()


def test_create_enforces_field_rule_required():
    _delete_test_rules()
    try:
        _insert_field_rule("description", "required", "")
        _invalidate_cache()

        result = create_document(DOCTYPE, {"module_name": "TestModule", "app_name": "core"})
        assert result["success"] is False
        assert "Field rule validation failed" in result["error"]
    finally:
        _delete_test_rules()
        _invalidate_cache()


def test_create_passes_field_rule_validation():
    _delete_test_rules()
    doc_name = None
    try:
        _insert_field_rule("module_name", "min_length", "2")
        _invalidate_cache()

        result = create_document(DOCTYPE, {"module_name": "CRUDEngine", "app_name": "core"})
        assert result["success"] is True
        doc_name = result["data"]["name"]
    finally:
        if doc_name:
            _cleanup_doc(doc_name)
        _delete_test_rules()
        _invalidate_cache()


def test_create_applies_computed_field():
    _delete_test_rules()
    doc_name = None
    try:
        _insert_computed_field("label", '"Computed: " + module_name')
        _invalidate_cache()

        result = create_document(DOCTYPE, {"module_name": "TestComputed", "app_name": "core"})
        assert result["success"] is True
        doc_name = result["data"]["name"]

        doc = get_document(DOCTYPE, doc_name)
        assert doc is not None
        assert doc["label"] == "Computed: TestComputed"
    finally:
        if doc_name:
            _cleanup_doc(doc_name)
        _delete_test_rules()
        _invalidate_cache()


def test_create_computed_field_overrides_payload():
    _delete_test_rules()
    doc_name = None
    try:
        _insert_computed_field("label", '"Auto: " + module_name')
        _invalidate_cache()

        result = create_document(DOCTYPE, {
            "module_name": "OverrideTest", "app_name": "core", "label": "Manual Label"
        })
        assert result["success"] is True
        doc_name = result["data"]["name"]

        doc = get_document(DOCTYPE, doc_name)
        assert doc is not None
        assert doc["label"] == "Auto: OverrideTest"
    finally:
        if doc_name:
            _cleanup_doc(doc_name)
        _delete_test_rules()
        _invalidate_cache()


def test_create_field_rule_and_computed_field_together():
    _delete_test_rules()
    doc_name = None
    try:
        _insert_field_rule("module_name", "min_length", "3")
        _insert_computed_field("description", '"Auto description for " + module_name')
        _invalidate_cache()

        result = create_document(DOCTYPE, {"module_name": "XY", "app_name": "core"})
        assert result["success"] is False
        assert "Field rule validation failed" in result["error"]

        result = create_document(DOCTYPE, {"module_name": "CombinedTest", "app_name": "core"})
        assert result["success"] is True
        doc_name = result["data"]["name"]

        doc = get_document(DOCTYPE, doc_name)
        assert doc is not None
        assert doc["description"] == "Auto description for CombinedTest"
    finally:
        if doc_name:
            _cleanup_doc(doc_name)
        _delete_test_rules()
        _invalidate_cache()


def test_update_enforces_field_rule():
    _delete_test_rules()
    doc_name = None
    try:
        result = create_document(DOCTYPE, {"module_name": "UpdateRuleTest", "app_name": "core"})
        assert result["success"] is True
        doc_name = result["data"]["name"]

        _insert_field_rule("module_name", "min_length", "10")
        _invalidate_cache()

        result = update_document(DOCTYPE, doc_name, {"module_name": "Short"})
        assert result["success"] is False
        assert "Field rule validation failed" in result["error"]
    finally:
        if doc_name:
            _cleanup_doc(doc_name)
        _delete_test_rules()
        _invalidate_cache()


def test_update_passes_field_rule_validation():
    _delete_test_rules()
    doc_name = None
    try:
        result = create_document(DOCTYPE, {"module_name": "UpdatePassTest", "app_name": "core"})
        assert result["success"] is True
        doc_name = result["data"]["name"]

        _insert_field_rule("module_name", "min_length", "5")
        _invalidate_cache()

        result = update_document(DOCTYPE, doc_name, {"module_name": "LongEnoughNow"})
        assert result["success"] is True
    finally:
        if doc_name:
            _cleanup_doc(doc_name)
        _delete_test_rules()
        _invalidate_cache()


def test_update_applies_computed_field():
    _delete_test_rules()
    doc_name = None
    try:
        result = create_document(DOCTYPE, {"module_name": "UpdateCFTest", "app_name": "core"})
        assert result["success"] is True
        doc_name = result["data"]["name"]

        _insert_computed_field("label", '"Updated: " + module_name')
        _invalidate_cache()

        result = update_document(DOCTYPE, doc_name, {"module_name": "ChangedName"})
        assert result["success"] is True

        doc = get_document(DOCTYPE, doc_name)
        assert doc is not None
        assert doc["label"] == "Updated: ChangedName"
    finally:
        if doc_name:
            _cleanup_doc(doc_name)
        _delete_test_rules()
        _invalidate_cache()

from galaxy.config import load_site_config
from galaxy.core.crud import (
    create_document,
    get_crud_fields,
    get_doctype_for_crud,
    get_document,
    list_documents,
    validate_create_payload,
)
from galaxy.db.connection import get_engine
from sqlalchemy import text

DOCTYPE = "Module Def"


def _engine():
    _, site = load_site_config()
    return get_engine(site)


def _cleanup(name: str):
    engine = _engine()
    with engine.begin() as conn:
        conn.execute(text('DELETE FROM "tabModule Def" WHERE name = :n'), {"n": name})


def test_doctype_exists_for_crud():
    doctype = get_doctype_for_crud(DOCTYPE)
    assert doctype is not None
    assert doctype["migration_status"] == "applied"


def test_has_crud_fields():
    fields = get_crud_fields(DOCTYPE)
    fieldnames = [f["fieldname"] for f in fields]
    assert "module_name" in fieldnames
    assert "app_name" in fieldnames
    assert "enabled" in fieldnames


def test_validate_create_payload_accepts_valid():
    doctype = get_doctype_for_crud(DOCTYPE)
    fields = get_crud_fields(DOCTYPE)
    errors, cleaned = validate_create_payload(doctype, fields, {"module_name": "Test Module", "app_name": "core"})
    assert errors == []
    assert cleaned["module_name"] == "Test Module"
    assert cleaned["app_name"] == "core"


def test_validate_create_payload_rejects_unknown_field():
    doctype = get_doctype_for_crud(DOCTYPE)
    fields = get_crud_fields(DOCTYPE)
    errors, cleaned = validate_create_payload(doctype, fields, {"module_name": "X", "app_name": "core", "nonexistent_field": "boom"})
    assert "Unknown field: 'nonexistent_field'." in errors
    assert "nonexistent_field" not in cleaned


def test_validate_create_payload_rejects_missing_required():
    doctype = get_doctype_for_crud(DOCTYPE)
    fields = get_crud_fields(DOCTYPE)
    errors, _ = validate_create_payload(doctype, fields, {})
    assert any("Required field" in e for e in errors)


def test_create_document_success():
    result = create_document(DOCTYPE, {"module_name": "CRUD Test Module", "app_name": "core"})
    assert result["success"] is True
    assert result["data"]["doctype"] == DOCTYPE
    doc_name = result["data"]["name"]
    assert doc_name.startswith("Module Def-")
    try:
        doc = get_document(DOCTYPE, doc_name)
        assert doc is not None
        assert doc["module_name"] == "CRUD Test Module"
    finally:
        _cleanup(doc_name)


def test_create_document_duplicate_name():
    result = create_document(DOCTYPE, {"module_name": "Dup Module", "app_name": "core"})
    assert result["success"] is True
    doc_name = result["data"]["name"]
    try:
        result2 = create_document(DOCTYPE, {"name": doc_name, "module_name": "Dup Module 2", "app_name": "erp"})
        assert result2["success"] is False
        assert "already exists" in result2["error"]
    finally:
        _cleanup(doc_name)


def test_create_document_rejects_unknown_field():
    result = create_document(DOCTYPE, {"module_name": "X", "app_name": "core", "fake_field": "bogus"})
    assert result["success"] is False
    assert "Validation failed" in result["error"]


def test_create_document_rejects_empty_required():
    result = create_document(DOCTYPE, {"module_name": "", "app_name": "core"})
    assert result["success"] is False


def test_list_documents_returns_results():
    docs = list_documents(DOCTYPE, limit=5)
    assert isinstance(docs, list)
    assert len(docs) <= 5
    if docs:
        assert "name" in docs[0]
        assert "module_name" in docs[0]


def test_list_documents_respects_limit():
    all_docs = list_documents(DOCTYPE, limit=100)
    few_docs = list_documents(DOCTYPE, limit=2)
    if len(all_docs) >= 2:
        assert len(few_docs) == 2


def test_list_documents_respects_offset():
    docs_offset_0 = list_documents(DOCTYPE, limit=5, offset=0)
    docs_offset_2 = list_documents(DOCTYPE, limit=5, offset=2)
    if len(docs_offset_0) > 2 and len(docs_offset_2) > 0:
        assert docs_offset_0[2]["name"] == docs_offset_2[0]["name"]


def test_get_document_existing():
    docs = list_documents(DOCTYPE, limit=1)
    if docs:
        doc = get_document(DOCTYPE, docs[0]["name"])
        assert doc is not None
        assert doc["name"] == docs[0]["name"]


def test_get_document_not_found():
    doc = get_document(DOCTYPE, "Module Def-NONEXISTENT-XXXX")
    assert doc is None


def test_create_list_get_cycle():
    result = create_document(DOCTYPE, {"module_name": "Cycle Test Module", "app_name": "core"})
    assert result["success"] is True
    doc_name = result["data"]["name"]
    try:
        docs = list_documents(DOCTYPE, limit=100)
        names = [d["name"] for d in docs]
        assert doc_name in names
        doc = get_document(DOCTYPE, doc_name)
        assert doc is not None
        assert doc["module_name"] == "Cycle Test Module"
    finally:
        _cleanup(doc_name)


def test_doctype_not_migrated():
    result = create_document("NonExistent", {"name": "X"})
    assert result.get("success") is False
    assert "not found" in result.get("error", "")


def test_create_document_coercion():
    result = create_document(DOCTYPE, {"module_name": "  Trimmed Module  ", "app_name": "core"})
    assert result["success"] is True
    doc_name = result["data"]["name"]
    try:
        doc = get_document(DOCTYPE, doc_name)
        assert doc is not None
        assert doc["module_name"] == "  Trimmed Module  "
    finally:
        _cleanup(doc_name)

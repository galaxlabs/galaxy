from sqlalchemy import text

from apps.galaxy.galaxy.core.crud import (
    create_document,
    get_crud_fields,
    get_doctype_for_crud,
    get_document,
    list_documents,
    validate_create_payload,
)
from apps.galaxy.galaxy.db.connection import get_engine
from internal.config.site_config import load_site_config

SUPPLIER = "Supplier"


def _engine():
    _, site = load_site_config()
    return get_engine(site)


def _cleanup(name: str):
    engine = _engine()
    with engine.begin() as conn:
        conn.execute(text('DELETE FROM "tabSupplier" WHERE name = :n'), {"n": name})


def test_supplier_doctype_exists_for_crud():
    doctype = get_doctype_for_crud(SUPPLIER)
    assert doctype is not None
    assert doctype["migration_status"] == "applied"


def test_supplier_has_crud_fields():
    fields = get_crud_fields(SUPPLIER)
    fieldnames = [f["fieldname"] for f in fields]
    assert "supplier_name" in fieldnames
    assert "status" in fieldnames


def test_validate_create_payload_accepts_valid():
    doctype = get_doctype_for_crud(SUPPLIER)
    fields = get_crud_fields(SUPPLIER)
    errors, cleaned = validate_create_payload(doctype, fields, {"supplier_name": "Test Co", "status": "Active"})
    assert errors == []
    assert cleaned["supplier_name"] == "Test Co"
    assert cleaned["status"] == "Active"


def test_validate_create_payload_rejects_unknown_field():
    doctype = get_doctype_for_crud(SUPPLIER)
    fields = get_crud_fields(SUPPLIER)
    errors, cleaned = validate_create_payload(doctype, fields, {"supplier_name": "X", "nonexistent_field": "boom"})
    assert "Unknown field: 'nonexistent_field'." in errors
    assert "nonexistent_field" not in cleaned


def test_validate_create_payload_rejects_missing_required():
    doctype = get_doctype_for_crud(SUPPLIER)
    fields = get_crud_fields(SUPPLIER)
    errors, _ = validate_create_payload(doctype, fields, {"status": "Active"})
    assert any("Required field" in e for e in errors)
    assert any("supplier_name" in e for e in errors)


def test_create_document_success():
    result = create_document(SUPPLIER, {"supplier_name": "CRUD Test Co", "status": "Active"})
    assert result["success"] is True
    assert result["data"]["doctype"] == SUPPLIER
    doc_name = result["data"]["name"]
    assert doc_name.startswith("Supplier-")
    try:
        doc = get_document(SUPPLIER, doc_name)
        assert doc is not None
        assert doc["supplier_name"] == "CRUD Test Co"
    finally:
        _cleanup(doc_name)


def test_create_document_duplicate_name():
    result = create_document(SUPPLIER, {"supplier_name": "Dup Co", "status": "Active"})
    assert result["success"] is True
    doc_name = result["data"]["name"]
    try:
        result2 = create_document(SUPPLIER, {"name": doc_name, "supplier_name": "Dup Co 2", "status": "Inactive"})
        assert result2["success"] is False
        assert "already exists" in result2["error"]
    finally:
        _cleanup(doc_name)


def test_create_document_rejects_unknown_field():
    result = create_document(SUPPLIER, {"supplier_name": "X", "status": "Active", "fake_field": "bogus"})
    assert result["success"] is False
    assert "Validation failed" in result["error"]


def test_create_document_rejects_empty_required():
    result = create_document(SUPPLIER, {"supplier_name": "", "status": "Active"})
    assert result["success"] is False


def test_list_documents_returns_results():
    docs = list_documents(SUPPLIER, limit=5)
    assert isinstance(docs, list)
    assert len(docs) <= 5
    if docs:
        assert "name" in docs[0]
        assert "supplier_name" in docs[0]


def test_list_documents_respects_limit():
    all_docs = list_documents(SUPPLIER, limit=100)
    few_docs = list_documents(SUPPLIER, limit=2)
    if len(all_docs) >= 2:
        assert len(few_docs) == 2


def test_list_documents_respects_offset():
    docs_offset_0 = list_documents(SUPPLIER, limit=5, offset=0)
    docs_offset_2 = list_documents(SUPPLIER, limit=5, offset=2)
    if len(docs_offset_0) > 2 and len(docs_offset_2) > 0:
        assert docs_offset_0[2]["name"] == docs_offset_2[0]["name"]


def test_get_document_existing():
    docs = list_documents(SUPPLIER, limit=1)
    if docs:
        doc = get_document(SUPPLIER, docs[0]["name"])
        assert doc is not None
        assert doc["name"] == docs[0]["name"]


def test_get_document_not_found():
    doc = get_document(SUPPLIER, "Supplier-NONEXISTENT-XXXX")
    assert doc is None


def test_create_list_get_cycle():
    result = create_document(SUPPLIER, {"supplier_name": "Cycle Test", "status": "Active"})
    assert result["success"] is True
    doc_name = result["data"]["name"]
    try:
        docs = list_documents(SUPPLIER, limit=100)
        names = [d["name"] for d in docs]
        assert doc_name in names
        doc = get_document(SUPPLIER, doc_name)
        assert doc is not None
        assert doc["supplier_name"] == "Cycle Test"
        assert doc["status"] == "Active"
    finally:
        _cleanup(doc_name)


def test_doctype_not_migrated():
    result = create_document("NonExistent", {"name": "X"})
    assert result.get("success") is False
    assert "not found" in result.get("error", "")


def test_create_document_supplier_name_coercion():
    result = create_document(SUPPLIER, {"supplier_name": "  Trimmed  ", "status": "Active"})
    assert result["success"] is True
    doc_name = result["data"]["name"]
    try:
        doc = get_document(SUPPLIER, doc_name)
        assert doc is not None
        assert doc["supplier_name"] == "  Trimmed  "
    finally:
        _cleanup(doc_name)

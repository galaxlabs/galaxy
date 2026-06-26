import pytest
from starlette.testclient import TestClient

from galaxy.app import app
from galaxy.model.field_type_registry import (
    register_type, get_type, get_all_types, coerce, sql_type,
    is_valid, options_required, skip_in_crud, is_sortable, FieldTypeDef,
)


class TestFieldTypeRegistry:
    def test_builtin_types_have_expected_names(self):
        types = get_all_types()
        for name in ("Data", "Int", "Float", "Currency", "Check", "Select", "Link", "Table"):
            assert name in types

    def test_get_type_known(self):
        td = get_type("Int")
        assert td is not None
        assert td.python_type is int
        assert td.sql_type == "INTEGER"

    def test_get_type_unknown(self):
        assert get_type("Nonexistent") is None

    def test_is_valid(self):
        assert is_valid("Data") is True
        assert is_valid("Int") is True
        assert is_valid("Bogus") is False

    def test_coerce_int(self):
        assert coerce("Int", "42") == 42
        assert coerce("Int", 42) == 42
        assert coerce("Int", 0) == 0

    def test_coerce_float(self):
        assert coerce("Float", "3.14") == 3.14
        assert coerce("Currency", "99.99") == 99.99

    def test_coerce_check(self):
        assert coerce("Check", True) == 1
        assert coerce("Check", False) == 0
        assert coerce("Check", None) == 0

    def test_coerce_json(self):
        val = coerce("JSON", {"a": 1})
        assert isinstance(val, str)
        assert "a" in val

    def test_coerce_date(self):
        from datetime import date
        d = date(2026, 6, 26)
        assert coerce("Date", d) == "2026-06-26"

    def test_coerce_str_pass_through(self):
        assert coerce("Data", "hello") == "hello"
        assert coerce("Data", None) is None

    def test_coerce_int_invalid(self):
        with pytest.raises(ValueError):
            coerce("Int", "not_a_number")

    def test_sql_type_mapping(self):
        assert sql_type("Data") == "TEXT"
        assert sql_type("Int") == "INTEGER"
        assert sql_type("Float") == "DOUBLE PRECISION"
        assert sql_type("Check") == "SMALLINT"
        assert sql_type("Date") == "DATE"
        assert sql_type("Datetime") == "TIMESTAMP"
        assert sql_type("JSON") == "JSONB"
        assert sql_type("Unknown") == "TEXT"

    def test_options_required(self):
        assert options_required("Link") is True
        assert options_required("Select") is True
        assert options_required("Table") is True
        assert options_required("Data") is False

    def test_skip_in_crud(self):
        assert skip_in_crud("Table") is True
        assert skip_in_crud("Data") is False

    def test_is_sortable(self):
        assert is_sortable("Data") is True
        assert is_sortable("Small Text") is False
        assert is_sortable("Table") is False

    def test_register_custom_type(self):
        td = FieldTypeDef("MyType", str, "TEXT")
        register_type(td)
        assert get_type("MyType") is td
        assert is_valid("MyType") is True

    def test_all_builtins_are_loaded(self):
        types = get_all_types()
        assert len(types) >= 15


class TestExportEngine:
    def test_export_csv_requires_auth(self, client):
        resp = client.get("/api/resource/DocType/export?format=csv")
        assert resp.status_code == 401

    def test_export_json_requires_auth(self, client):
        resp = client.get("/api/resource/DocType/export?format=json")
        assert resp.status_code == 401

    def test_export_without_session_returns_401(self, client):
        resp = client.get("/api/resource/DocType/export")
        assert resp.status_code == 401

    def test_export_unsupported_format(self, authed_client):
        resp = authed_client.get("/api/resource/DocType/export?format=pdf")
        assert resp.status_code == 400
        assert "Unsupported" in resp.json()["error"]

    def test_export_csv_returns_text(self, authed_client):
        resp = authed_client.get("/api/resource/DocType/export?format=csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
        assert resp.headers["content-disposition"].startswith("attachment")
        assert resp.text.startswith("name")

    def test_export_json_returns_json(self, authed_client):
        resp = authed_client.get("/api/resource/DocType/export?format=json")
        assert resp.status_code == 200
        assert "application/json" in resp.headers["content-type"]
        assert resp.headers["content-disposition"].startswith("attachment")
        import json
        data = json.loads(resp.text)
        assert isinstance(data, list)

    def test_export_csv_with_search(self, authed_client):
        resp = authed_client.get("/api/resource/DocType/export?format=csv&search=Test")
        assert resp.status_code == 200
        assert resp.text.startswith("name")

    def test_export_csv_with_limit(self, authed_client):
        resp = authed_client.get("/api/resource/DocType/export?format=csv&limit=5")
        assert resp.status_code == 200
        lines = resp.text.strip().split("\n")
        assert len(lines) <= 6

    @pytest.fixture
    def authed_client(self, client):
        from galaxy.auth import create_session
        session = create_session("Administrator")
        client.cookies.set("galaxy_session", session)
        return client

    @pytest.fixture
    def client(self):
        return TestClient(app)

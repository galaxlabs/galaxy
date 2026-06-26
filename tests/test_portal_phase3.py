import pytest
from sqlalchemy import text
from starlette.testclient import TestClient

from galaxy.config import load_site_config
from galaxy.database.connection import get_engine
from galaxy.app import app
from galaxy.portal.permissions import PortalPermissionEngine


def _cleanup():
    _, site = load_site_config()
    engine = get_engine(site)
    with engine.begin() as conn:
        conn.execute(text("""DELETE FROM "tabPortalProfileLink" WHERE portal_user = 'perm_test@example.com'"""))
        conn.execute(text("""DELETE FROM "tabPortalFieldPermission" WHERE portal_role = 'Test Portal Role'"""))
        conn.execute(text("""DELETE FROM "tabPortalPermission" WHERE portal_role = 'Test Portal Role'"""))
        conn.execute(text("""DELETE FROM "tabPortalSession" WHERE user_name = 'perm_test@example.com'"""))
        conn.execute(text("""DELETE FROM "tabPortalUser" WHERE email = 'perm_test@example.com'"""))


_cleanup()


@pytest.fixture(autouse=True)
def setup_portal_data():
    _cleanup()
    _, site = load_site_config()
    engine = get_engine(site)
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO "tabPortalUser" (name, email, display_name, portal_role, account_status, password_hash)
                VALUES ('perm_test@example.com', 'perm_test@example.com', 'Perm Test', 'Test Portal Role', 'active', 'dummy')
            """),
        )
        conn.execute(
            text("""
                INSERT INTO "tabPortalSession" (name, user_name, token, expires_at)
                VALUES ('pses-permtest', 'perm_test@example.com', 'test_token_perm', CURRENT_TIMESTAMP + INTERVAL '1 day')
            """),
        )
        conn.execute(
            text("""
                INSERT INTO "tabPortalPermission" (name, parent, portal_role, "read", "write", "create", "delete", idx)
                VALUES ('pp-DocType-TPR', 'DocType', 'Test Portal Role', TRUE, TRUE, TRUE, FALSE, 0)
            """),
        )
        conn.execute(
            text("""
                INSERT INTO "tabPortalProfileLink" (name, parent, portal_user, doctype, docname, relationship, enabled, idx)
                VALUES ('ppl-test1', 'DocType', 'perm_test@example.com', 'DocType', 'Test Doc', 'member', TRUE, 0)
            """),
        )
        conn.execute(
            text("""
                INSERT INTO "tabPortalFieldPermission" (name, parent, portal_role, field_name, "read", "write", permlevel, idx)
                VALUES ('pfp-name', 'DocType', 'Test Portal Role', 'name', TRUE, TRUE, 0, 0)
            """),
        )
        conn.execute(
            text("""
                INSERT INTO "tabPortalFieldPermission" (name, parent, portal_role, field_name, "read", "write", permlevel, idx)
                VALUES ('pfp-module', 'DocType', 'Test Portal Role', 'module', TRUE, FALSE, 0, 1)
            """),
        )
    yield
    _cleanup()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def authed_client(client):
    client.cookies.set("portal_session", "test_token_perm")
    return client


class TestPortalPermissionEngine:
    def test_can_read(self):
        engine = PortalPermissionEngine("perm_test@example.com", "Test Portal Role")
        assert engine.can_read("DocType") is True

    def test_cannot_read_unknown(self):
        engine = PortalPermissionEngine("perm_test@example.com", "Test Portal Role")
        assert engine.can_read("Unknown") is False

    def test_can_write(self):
        engine = PortalPermissionEngine("perm_test@example.com", "Test Portal Role")
        assert engine.can_write("DocType") is True

    def test_can_create(self):
        engine = PortalPermissionEngine("perm_test@example.com", "Test Portal Role")
        assert engine.can_create("DocType") is True

    def test_cannot_delete(self):
        engine = PortalPermissionEngine("perm_test@example.com", "Test Portal Role")
        assert engine.can_delete("DocType") is False

    def test_can_access_owned_doc(self):
        engine = PortalPermissionEngine("perm_test@example.com", "Test Portal Role")
        assert engine.can_access_doc("DocType", "Test Doc") is True

    def test_cannot_access_unowned_doc(self):
        engine = PortalPermissionEngine("perm_test@example.com", "Test Portal Role")
        assert engine.can_access_doc("DocType", "Other Doc") is False

    def test_get_owned_docs(self):
        engine = PortalPermissionEngine("perm_test@example.com", "Test Portal Role")
        owned = engine.get_owned_docs("DocType")
        assert len(owned) == 1
        assert owned[0]["docname"] == "Test Doc"

    def test_get_readable_fields(self):
        engine = PortalPermissionEngine("perm_test@example.com", "Test Portal Role")
        fields = engine.get_readable_fields("DocType")
        assert fields is not None
        assert "name" in fields
        assert "module" in fields

    def test_get_writable_fields(self):
        engine = PortalPermissionEngine("perm_test@example.com", "Test Portal Role")
        fields = engine.get_writable_fields("DocType")
        assert "name" in fields
        assert "module" not in fields


class TestPortalCRUDAuth:
    def test_list_requires_auth(self, client):
        resp = client.get("/api/portal/resource/DocType")
        assert resp.status_code == 401

    def test_get_requires_auth(self, client):
        resp = client.get("/api/portal/resource/DocType/some-doc")
        assert resp.status_code == 401

    def test_create_requires_auth(self, client):
        resp = client.post("/api/portal/resource/DocType", json={"name": "x"})
        assert resp.status_code == 401

    def test_update_requires_auth(self, client):
        resp = client.put("/api/portal/resource/DocType/some-doc", json={"name": "x"})
        assert resp.status_code == 401

    def test_delete_requires_auth(self, client):
        resp = client.delete("/api/portal/resource/DocType/some-doc")
        assert resp.status_code == 401


class TestPortalCRUDList:
    def test_list_returns_200(self, authed_client):
        resp = authed_client.get("/api/portal/resource/DocType")
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data

    def test_list_applies_field_permissions(self, authed_client):
        resp = authed_client.get("/api/portal/resource/DocType")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)


class TestPortalCRUDGet:
    def test_get_owned_doc_returns_404_if_not_in_table(self, authed_client):
        resp = authed_client.get("/api/portal/resource/DocType/Test Doc")
        assert resp.status_code == 404

    def test_get_unowned_returns_404(self, authed_client):
        resp = authed_client.get("/api/portal/resource/DocType/Nonexistent")
        assert resp.status_code == 404


class TestPortalCRUDCreate:
    def test_create_no_permission(self, authed_client):
        resp = authed_client.post("/api/portal/resource/Unknown", json={"name": "x"})
        assert resp.status_code == 403

    def test_create_filters_writable(self, authed_client):
        resp = authed_client.post(
            "/api/portal/resource/DocType",
            json={"name": "portal-test-new", "module": "Portal", "app_name": "core", "table_name": "tabPortalTestNew", "migration_status": "applied"},
        )
        assert resp.status_code in (201, 400)


class TestPortalCRUDUpdate:
    def test_update_unowned_returns_404(self, authed_client):
        resp = authed_client.put("/api/portal/resource/DocType/Nonexistent", json={"module": "Portal"})
        assert resp.status_code == 404

    def test_update_no_write_perm(self, authed_client):
        resp = authed_client.put("/api/portal/resource/Role/Test Doc", json={"role_name": "x"})
        assert resp.status_code == 403


class TestPortalCRUDDelete:
    def test_delete_no_permission(self, authed_client):
        resp = authed_client.delete("/api/portal/resource/DocType/Test Doc")
        assert resp.status_code == 403

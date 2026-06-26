import pytest
from sqlalchemy import text
from starlette.testclient import TestClient

from galaxy.config import load_site_config
from galaxy.database.connection import get_engine
from galaxy.app import app


def _cleanup_test_user():
    _, site = load_site_config()
    engine = get_engine(site)
    with engine.begin() as conn:
        conn.execute(text("""DELETE FROM "tabPortalUser" WHERE email = 'portal_test@example.com'"""))
        conn.execute(text("""DELETE FROM "tabPortalSession" WHERE user_name = 'portal_test@example.com'"""))


_cleanup_test_user()


@pytest.fixture
def client():
    return TestClient(app)


TEST_EMAIL = "portal_test@example.com"
TEST_PASS = "secret123"


class TestPortalSignup:
    def test_signup_success(self, client):
        _cleanup_test_user()
        resp = client.post("/api/portal/auth/signup", json={
            "email": TEST_EMAIL,
            "password": TEST_PASS,
            "display_name": "Portal Test",
        })
        data = resp.json()
        assert resp.status_code == 200
        assert data["success"] is True
        assert data["user"]["email"] == TEST_EMAIL

    def test_signup_duplicate(self, client):
        resp = client.post("/api/portal/auth/signup", json={
            "email": TEST_EMAIL,
            "password": TEST_PASS,
        })
        assert resp.status_code == 409
        assert resp.json()["success"] is False

    def test_signup_missing_fields(self, client):
        resp = client.post("/api/portal/auth/signup", json={
            "email": "",
            "password": "",
        })
        assert resp.status_code == 400

    def test_signup_short_password(self, client):
        resp = client.post("/api/portal/auth/signup", json={
            "email": "short@pw.com",
            "password": "123",
        })
        assert resp.status_code == 400


class TestPortalLogin:
    def test_login_success(self, client):
        resp = client.post("/api/portal/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASS,
        })
        data = resp.json()
        assert resp.status_code == 200
        assert data["success"] is True
        assert "token" in data
        assert data["user"]["email"] == TEST_EMAIL

    def test_login_wrong_password(self, client):
        resp = client.post("/api/portal/auth/login", json={
            "email": TEST_EMAIL,
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    def test_login_nonexistent(self, client):
        resp = client.post("/api/portal/auth/login", json={
            "email": "nobody@nowhere.com",
            "password": TEST_PASS,
        })
        assert resp.status_code == 401

    def test_login_missing_fields(self, client):
        resp = client.post("/api/portal/auth/login", json={
            "email": "",
            "password": "",
        })
        assert resp.status_code == 400


class TestPortalAuthMe:
    def test_auth_me_without_session(self, client):
        resp = client.get("/api/portal/auth/me")
        assert resp.status_code == 401

    def test_auth_me_with_session(self, client):
        login_resp = client.post("/api/portal/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASS,
        })
        token = login_resp.json()["token"]
        resp = client.get("/api/portal/auth/me", cookies={"portal_session": token})
        data = resp.json()
        assert resp.status_code == 200
        assert data["success"] is True
        assert data["user"]["email"] == TEST_EMAIL

    def test_auth_me_with_invalid_token(self, client):
        resp = client.get("/api/portal/auth/me", cookies={"portal_session": "invalidtoken"})
        assert resp.status_code == 401


class TestPortalLogout:
    def test_logout_invalidates_session(self, client):
        login_resp = client.post("/api/portal/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASS,
        })
        token = login_resp.json()["token"]
        client.post("/api/portal/auth/logout", cookies={"portal_session": token})
        resp = client.get("/api/portal/auth/me", cookies={"portal_session": token})
        assert resp.status_code == 401

    def test_logout_without_session_safe(self, client):
        resp = client.post("/api/portal/auth/logout")
        assert resp.status_code == 200


class TestPortalProfile:
    def test_profile_without_session(self, client):
        resp = client.get("/api/portal/profile")
        assert resp.status_code == 401

    def test_profile_with_session(self, client):
        login_resp = client.post("/api/portal/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASS,
        })
        token = login_resp.json()["token"]
        resp = client.get("/api/portal/profile", cookies={"portal_session": token})
        data = resp.json()
        assert resp.status_code == 200
        assert data["success"] is True
        assert data["profile"]["email"] == TEST_EMAIL


class TestPortalPages:
    def test_portal_home_public(self, client):
        resp = client.get("/portal", follow_redirects=False)
        assert resp.status_code == 200

    def test_portal_login_page_public(self, client):
        resp = client.get("/portal/login", follow_redirects=False)
        assert resp.status_code == 200

    def test_portal_signup_page_public(self, client):
        resp = client.get("/portal/signup", follow_redirects=False)
        assert resp.status_code == 200

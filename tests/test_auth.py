from sqlalchemy import text
from starlette.testclient import TestClient

from internal.config.site_config import load_site_config
from internal.core.auth import create_session, delete_session, get_session, verify_password
from internal.db.connection import get_engine
from internal.http.server import app


def _clean_session(token):
    engine = _get_engine()
    with engine.begin() as conn:
        conn.execute(
            text('DELETE FROM "tabSession" WHERE token = :token'),
            {"token": token},
        )


def _get_engine():
    _, site = load_site_config()
    return get_engine(site)


client = TestClient(app)


def test_verify_password_correct():
    user = verify_password("Administrator", "admin")
    assert user is not None
    assert user["username"] == "Administrator"
    assert "password_hash" not in user


def test_verify_password_wrong():
    user = verify_password("Administrator", "wrongpassword")
    assert user is None


def test_verify_password_nonexistent():
    user = verify_password("NonExistentUser", "admin")
    assert user is None


def test_create_and_get_session():
    token = create_session("Administrator")
    assert token is not None
    assert len(token) > 20
    try:
        session = get_session(token)
        assert session is not None
        assert session["username"] == "Administrator"
    finally:
        _clean_session(token)


def test_get_session_invalid_token():
    session = get_session("invalid-token-that-does-not-exist")
    assert session is None


def test_delete_session():
    token = create_session("Administrator")
    session = get_session(token)
    assert session is not None
    delete_session(token)
    session_after = get_session(token)
    assert session_after is None


def test_desk_redirects_to_login_without_session():
    resp = client.get("/desk", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/login"


def test_api_resource_returns_401_without_session():
    resp = client.get("/api/resource/Supplier")
    assert resp.status_code == 401
    data = resp.json()
    assert data["success"] is False
    assert data["error"] == "Authentication required."


def test_login_then_auth_me():
    login_resp = client.post("/api/auth/login", json={"username": "Administrator", "password": "admin"})
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert data["success"] is True
    assert data["data"]["user"]["username"] == "Administrator"

    me_resp = client.get("/api/auth/me", cookies=login_resp.cookies)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["success"] is True
    assert me_data["data"]["user"]["username"] == "Administrator"


def test_login_then_protected_api():
    login_resp = client.post("/api/auth/login", json={"username": "Administrator", "password": "admin"})
    assert login_resp.status_code == 200

    resp = client.get("/api/resource/Supplier", cookies=login_resp.cookies)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True


def test_login_then_desk():
    login_resp = client.post("/api/auth/login", json={"username": "Administrator", "password": "admin"})
    assert login_resp.status_code == 200

    resp = client.get("/desk", cookies=login_resp.cookies)
    assert resp.status_code == 200

from galaxy.auth import create_session, delete_session, get_session, verify_password
from galaxy.config import load_site_config
from galaxy.db.connection import get_engine
from galaxy.server import app
from sqlalchemy import text
from starlette.testclient import TestClient


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


def test_invalid_session_cookie_returns_401():
    resp = client.get("/api/resource/Supplier", cookies={"galaxy_session": "invalid-random-token-value"})
    assert resp.status_code == 401
    data = resp.json()
    assert data["success"] is False
    assert data["error"] == "Authentication required."


def test_expired_session_is_rejected():
    engine = _get_engine()
    from datetime import UTC, datetime, timedelta
    expired_token = "expired-test-token-12345"
    past = datetime.now(UTC) - timedelta(hours=1)
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO "tabSession" (name, user_name, token, expires_at, idx)
                VALUES (:name, :user_name, :token, :expires_at, 0)
            """),
            {"name": "expired-session-test", "user_name": "Administrator",
             "token": expired_token, "expires_at": past},
        )
    try:
        resp = client.get("/api/resource/Supplier", cookies={"galaxy_session": expired_token})
        assert resp.status_code == 401
        data = resp.json()
        assert data["success"] is False
        assert data["error"] == "Authentication required."
    finally:
        with engine.begin() as conn:
            conn.execute(
                text('DELETE FROM "tabSession" WHERE token = :token'),
                {"token": expired_token},
            )


def test_logout_invalidates_session():
    login_resp = client.post("/api/auth/login", json={"username": "Administrator", "password": "admin"})
    assert login_resp.status_code == 200
    cookie_jar = login_resp.cookies

    resp_before = client.get("/api/resource/Supplier", cookies=cookie_jar)
    assert resp_before.status_code == 200

    logout_resp = client.post("/api/auth/logout", cookies=cookie_jar)
    assert logout_resp.status_code == 200

    resp_after = client.get("/api/resource/Supplier", cookies=cookie_jar)
    assert resp_after.status_code == 401
    data = resp_after.json()
    assert data["success"] is False
    assert data["error"] == "Authentication required."


# ── Additional Step 2 route protection tests ─────────────────────


def test_desk_doctypes_redirects_without_session():
    resp = client.get("/desk/doctypes", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/login"


def test_api_resource_post_returns_401_without_session():
    resp = client.post("/api/resource/Supplier", json={"supplier_name": "Test"})
    assert resp.status_code == 401
    data = resp.json()
    assert data["success"] is False
    assert data["error"] == "Authentication required."


def test_migration_apply_returns_401_without_session():
    resp = client.post("/api/migration/doctype/Customer/apply")
    assert resp.status_code == 401
    data = resp.json()
    assert data["success"] is False
    assert data["error"] == "Authentication required."


def test_health_public():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("ok", "degraded")


def test_api_version_public():
    resp = client.get("/api/version")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "galaxy"


def test_login_page_public():
    resp = client.get("/login")
    assert resp.status_code == 200
    assert "login" in resp.text.lower()


def test_logout_without_session_safe():
    resp = client.post("/api/auth/logout")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True


def test_migration_preview_public():
    """Migration preview is read-only, should be accessible without auth."""
    resp = client.get("/api/migration/doctype/Supplier/preview")
    assert resp.status_code == 200


def test_protected_desk_builder_redirects_without_session():
    resp = client.get("/desk/builder/doctype/new", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/login"


def test_core_scripts_protected():
    """POST to /api/core/scripts should require auth."""
    resp = client.post("/api/core/scripts", json={})
    assert resp.status_code == 401
    data = resp.json()
    assert data["success"] is False


def test_login_session_works_for_report():
    """A protected report route requires session."""
    resp = client.get("/api/report/NonExistent", follow_redirects=False)
    assert resp.status_code == 401


# ── Permission tests ─────────────────────────────────────────────


def test_authorize_no_user_returns_false():
    from galaxy.permissions import authorize
    ok, msg = authorize("Supplier", None, "read")
    assert ok is False
    assert msg == "Authentication required."


def test_authorize_empty_user_returns_false():
    from galaxy.permissions import authorize
    ok, msg = authorize("Supplier", "", "read")
    assert ok is False
    assert msg == "Authentication required."


def test_authorize_administrator_can_read_any_doctype():
    from galaxy.permissions import authorize
    ok, msg = authorize("NonExistentDocType", "Administrator", "read")
    assert ok is True
    assert msg == ""


def test_authorize_administrator_can_create():
    from galaxy.permissions import authorize
    ok, _ = authorize("Supplier", "Administrator", "create")
    assert ok is True


def test_authorize_administrator_can_write():
    from galaxy.permissions import authorize
    ok, _ = authorize("Supplier", "Administrator", "write")
    assert ok is True


def test_authorize_administrator_can_delete():
    from galaxy.permissions import authorize
    ok, _ = authorize("Supplier", "Administrator", "delete")
    assert ok is True


def test_get_user_roles_administrator():
    from galaxy.permissions import get_user_roles
    roles = get_user_roles("Administrator")
    assert "System Manager" in roles


def test_get_user_roles_unknown():
    from galaxy.permissions import get_user_roles
    roles = get_user_roles("NonExistentUser")
    assert roles == []


def test_user_has_role_administrator():
    from galaxy.permissions import user_has_role
    assert user_has_role("Administrator", "System Manager") is True


def test_user_has_role_unknown():
    from galaxy.permissions import user_has_role
    assert user_has_role("NonExistentUser", "System Manager") is False


def test_x_galaxy_user_header_bypass_removed():
    """X-Galaxy-User header should not bypass authentication."""
    resp = client.get("/api/resource/Supplier", headers={"X-Galaxy-User": "Administrator"})
    assert resp.status_code == 401
    data = resp.json()
    assert data["success"] is False


def test_x_galaxy_user_header_does_not_work_on_desk():
    """X-Galaxy-User header should not bypass Desk redirect."""
    resp = client.get("/desk", headers={"X-Galaxy-User": "Administrator"}, follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/login"

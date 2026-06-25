
from sqlalchemy import text

from internal.config.site_config import load_site_config
from internal.core.auth import create_session, delete_session, get_session, verify_password
from internal.db.connection import get_engine


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

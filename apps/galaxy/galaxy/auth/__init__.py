import secrets
from datetime import UTC, datetime, timedelta

from passlib.hash import bcrypt as passlib_bcrypt
from sqlalchemy import text

from galaxy.config import load_site_config
from galaxy.core.tenant import current_tenant
from galaxy.db.connection import get_engine


def _get_engine():
    _, site = load_site_config()
    return get_engine(site)


def verify_password(username: str, password: str) -> dict | None:
    tenant_id = current_tenant.get()
    engine = _get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text('SELECT name, username, email, password_hash, enabled FROM "tabUser" WHERE username = :username AND tenant_id = :tenant_id'),
            {"username": username, "tenant_id": tenant_id},
        ).mappings().one_or_none()

    if row is None:
        return None

    user = dict(row)
    if not user.get("enabled", True):
        return None

    if not passlib_bcrypt.verify(password, user["password_hash"]):
        return None

    del user["password_hash"]
    return user


def create_session(username: str) -> str:
    tenant_id = current_tenant.get()
    token = secrets.token_urlsafe(48)
    engine = _get_engine()
    name = f"ses-{token[:16]}"
    expires_at = datetime.now(UTC) + timedelta(hours=24)

    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO "tabSession" (name, user_name, token, tenant_id, expires_at, idx)
                VALUES (:name, :user_name, :token, :tenant_id, :expires_at, 0)
            """),
            {"name": name, "user_name": username, "token": token, "tenant_id": tenant_id, "expires_at": expires_at},
        )

    return token


def get_session(token: str) -> dict | None:
    tenant_id = current_tenant.get()
    engine = _get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT s.user_name, s.expires_at, u.name, u.username, u.email, u.enabled
                FROM "tabSession" s
                JOIN "tabUser" u ON s.user_name = u.name
                WHERE s.token = :token AND s.tenant_id = :tenant_id
            """),
            {"token": token, "tenant_id": tenant_id},
        ).mappings().one_or_none()

    if row is None:
        return None

    session = dict(row)
    expires_at = session["expires_at"]

    now = datetime.now(UTC)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)

    if now > expires_at:
        return None

    if not session.get("enabled", True):
        return None

    return {
        "name": session["name"],
        "username": session["username"],
        "email": session["email"],
    }


def delete_session(token: str) -> None:
    engine = _get_engine()
    with engine.begin() as conn:
        conn.execute(
            text('DELETE FROM "tabSession" WHERE token = :token'),
            {"token": token},
        )


def require_session(request) -> str | None:
    cookie = request.cookies.get("galaxy_session")
    if not cookie:
        return None
    session = get_session(cookie)
    if session is None:
        return None
    return session["username"]

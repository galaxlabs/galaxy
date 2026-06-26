import secrets
from datetime import UTC, datetime, timedelta

from passlib.hash import bcrypt as passlib_bcrypt
from sqlalchemy import text

from galaxy.config import load_site_config
from galaxy.database.connection import get_engine


def _get_engine():
    _, site = load_site_config()
    return get_engine(site)


def portal_signup(email: str, password: str, display_name: str | None = None) -> dict | None:
    engine = _get_engine()
    password_hash = passlib_bcrypt.hash(password)
    name = email.lower().strip()
    with engine.begin() as conn:
        existing = conn.execute(
            text("""SELECT COUNT(*) FROM "tabPortalUser" WHERE email = :email"""),
            {"email": name},
        ).scalar()
        if existing > 0:
            return None
        conn.execute(
            text("""
                INSERT INTO "tabPortalUser" (name, email, display_name, portal_role, account_status, password_hash, idx)
                VALUES (:name, :email, :display_name, :portal_role, :account_status, :password_hash, 0)
            """),
            {
                "name": name,
                "email": name,
                "display_name": display_name or name.split("@")[0],
                "portal_role": "Portal User",
                "account_status": "active",
                "password_hash": password_hash,
            },
        )
    return {"name": name, "email": name, "display_name": display_name or name.split("@")[0]}


def portal_verify_password(email: str, password: str) -> dict | None:
    engine = _get_engine()
    name = email.lower().strip()
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT name, email, display_name, portal_role, account_status,
                       email_verified, password_hash, language, timezone, avatar
                FROM "tabPortalUser" WHERE email = :email
            """),
            {"email": name},
        ).mappings().one_or_none()
    if row is None:
        return None
    user = dict(row)
    if user.get("account_status") != "active":
        return None
    if not passlib_bcrypt.verify(password, user["password_hash"]):
        return None
    del user["password_hash"]
    return user


def portal_create_session(email: str) -> str:
    token = secrets.token_urlsafe(48)
    engine = _get_engine()
    name = f"pses-{token[:16]}"
    expires_at = datetime.now(UTC) + timedelta(hours=24)
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO "tabPortalSession" (name, user_name, token, expires_at, idx)
                VALUES (:name, :user_name, :token, :expires_at, 0)
            """),
            {"name": name, "user_name": email.lower().strip(), "token": token, "expires_at": expires_at},
        )
    return token


def portal_get_session(token: str) -> dict | None:
    engine = _get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT s.name, s.user_name, s.expires_at,
                       u.email, u.display_name, u.portal_role, u.account_status
                FROM "tabPortalSession" s
                JOIN "tabPortalUser" u ON s.user_name = u.email
                WHERE s.token = :token
            """),
            {"token": token},
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
    if session.get("account_status") != "active":
        return None
    return {
        "name": session["name"],
        "email": session["email"],
        "display_name": session["display_name"],
        "portal_role": session["portal_role"],
    }


def portal_delete_session(token: str) -> None:
    engine = _get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""DELETE FROM "tabPortalSession" WHERE token = :token"""),
            {"token": token},
        )


def portal_require_session(request) -> dict | None:
    cookie = request.cookies.get("portal_session")
    if not cookie:
        return None
    return portal_get_session(cookie)

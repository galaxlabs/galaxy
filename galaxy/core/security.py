import hashlib
import hmac
import secrets
import time
from datetime import UTC, datetime

from sqlalchemy import text

from galaxy.db.connection import get_engine
from internal.config.site_config import load_common_config


def get_security_settings() -> dict:
    try:
        common = load_common_config()
    except Exception:
        common = {}
    return {
        "developer_mode": common.get("developer_mode", True),
        "allow_server_scripts": common.get("allow_server_scripts", False),
        "allow_query_reports": common.get("allow_query_reports", False),
        "allow_script_reports": common.get("allow_script_reports", False),
        "allow_dev_auth_bypass": common.get("allow_dev_auth_bypass", False),
        "csrf_enabled": common.get("csrf_enabled", True),
        "login_rate_limit_enabled": common.get("login_rate_limit_enabled", True),
        "login_rate_limit_max_attempts": common.get("login_rate_limit_max_attempts", 5),
        "login_rate_limit_window_seconds": common.get("login_rate_limit_window_seconds", 300),
    }


CSRF_SECRET: str | None = None


def _get_csrf_secret() -> str:
    global CSRF_SECRET
    if CSRF_SECRET is None:
        common = load_common_config()
        CSRF_SECRET = common.get("csrf_secret", secrets.token_hex(32))
    return CSRF_SECRET


def generate_csrf_token(session_token: str) -> str:
    return hmac.new(
        _get_csrf_secret().encode(),
        session_token.encode(),
        hashlib.sha256,
    ).hexdigest()


def validate_csrf_token(session_token: str, provided_token: str) -> bool:
    expected = generate_csrf_token(session_token)
    return hmac.compare_digest(expected, provided_token)


_login_attempts: dict[str, list[float]] = {}


def check_login_rate_limit(ip: str, username: str) -> tuple[bool, str]:
    sec = get_security_settings()
    if not sec["login_rate_limit_enabled"]:
        return True, ""

    key = f"{ip}:{username}"
    now = time.time()
    window = sec["login_rate_limit_window_seconds"]
    max_attempts = sec["login_rate_limit_max_attempts"]

    attempts = _login_attempts.get(key, [])
    attempts = [t for t in attempts if now - t < window]

    if len(attempts) >= max_attempts:
        return False, "Too many login attempts. Please try again later."

    attempts.append(now)
    _login_attempts[key] = attempts
    return True, ""


def clear_login_rate_limit(ip: str, username: str):
    key = f"{ip}:{username}"
    _login_attempts.pop(key, None)


def log_security_event(event: str, user: str | None, message: str, source: str, ip_address: str | None = None):
    try:
        from internal.config.site_config import load_site_config

        _, site = load_site_config()
        engine = get_engine(site)
        ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")[:18]
        name = f"SEC-{ts}"
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO "tabError Log" (name, error_type, message, source, user_name, request_path, method, status, idx)
                    VALUES (:name, :error_type, :message, :source, :user_name, :request_path, :method, :status, 0)
                """),
                {
                    "name": name,
                    "error_type": "Security",
                    "message": f"[{event}] {message}",
                    "source": source,
                    "user_name": user or "System",
                    "request_path": ip_address or "",
                    "method": event,
                    "status": "Blocked",
                },
            )
    except Exception:
        pass

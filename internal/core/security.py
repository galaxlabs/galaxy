from datetime import UTC, datetime

from sqlalchemy import text

from internal.config.site_config import load_common_config
from internal.db.connection import get_engine


def get_security_settings() -> dict:
    try:
        common = load_common_config()
    except Exception:
        common = {}
    return {
        "developer_mode": common.get("developer_mode", True),
        "allow_server_scripts": common.get("allow_server_scripts", True),
        "allow_query_reports": common.get("allow_query_reports", True),
        "allow_script_reports": common.get("allow_script_reports", False),
    }


def log_security_event(event: str, user: str | None, message: str, source: str):
    try:
        from internal.config.site_config import load_site_config

        _, site = load_site_config()
        engine = get_engine(site)
        ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        name = f"SEC-{ts}"
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO "tabError Log" (name, error_type, message, source, user_name, status, idx)
                    VALUES (:name, :error_type, :message, :source, :user_name, :status, 0)
                """),
                {
                    "name": name,
                    "error_type": "Security",
                    "message": message,
                    "source": source,
                    "user_name": user or "System",
                    "status": "Blocked",
                },
            )
    except Exception:
        pass

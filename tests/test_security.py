from unittest.mock import patch

from sqlalchemy import text

from internal.config.site_config import load_site_config
from internal.core.report_engine import run_report
from internal.core.script_engine import run_scripts
from internal.core.security import get_security_settings, log_security_event
from internal.db.connection import get_engine


def _get_engine():
    _, site = load_site_config()
    return get_engine(site)


def test_security_settings_defaults():
    sec = get_security_settings()
    assert sec["developer_mode"] is True
    assert sec["allow_server_scripts"] is True
    assert sec["allow_query_reports"] is True
    assert sec["allow_script_reports"] is False


def test_log_security_event():
    log_security_event("test_event", "Administrator", "Test security log entry.", "test")
    engine = _get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("""SELECT error_type, message, source, user_name, status FROM "tabError Log" WHERE source = 'test' ORDER BY created_at DESC LIMIT 1""")
        ).mappings().one_or_none()
    assert row is not None
    assert row["error_type"] == "Security"
    assert row["user_name"] == "Administrator"
    assert row["status"] == "Blocked"
    with engine.begin() as conn:
        conn.execute(text("""DELETE FROM "tabError Log" WHERE source = 'test'"""))


@patch("internal.core.report_engine.get_security_settings")
def test_script_report_blocked(mock_sec):
    mock_sec.return_value = {
        "developer_mode": True,
        "allow_server_scripts": True,
        "allow_query_reports": True,
        "allow_script_reports": False,
    }
    engine = _get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO "tabReport" (name, ref_doctype, report_type, script, enabled, idx)
                VALUES ('test-sec-script-report', 'DocType', 'Script Report', 'result = [1,2,3]', TRUE, 0)
                ON CONFLICT (name) DO NOTHING
            """)
        )
    try:
        result = run_report("test-sec-script-report")
        assert result["success"] is False
        assert "disabled" in result["error"].lower()
    finally:
        with engine.begin() as conn:
            conn.execute(text("""DELETE FROM "tabReport" WHERE name = 'test-sec-script-report'"""))


@patch("internal.core.report_engine.get_security_settings")
def test_query_report_blocked(mock_sec):
    mock_sec.return_value = {
        "developer_mode": True,
        "allow_server_scripts": True,
        "allow_query_reports": False,
        "allow_script_reports": False,
    }
    engine = _get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO "tabReport" (name, ref_doctype, report_type, query, enabled, idx)
                VALUES ('test-sec-query-report', 'DocType', 'Query Report', 'SELECT 1 AS col', TRUE, 0)
                ON CONFLICT (name) DO NOTHING
            """)
        )
    try:
        result = run_report("test-sec-query-report")
        assert result["success"] is False
        assert "disabled" in result["error"].lower()
    finally:
        with engine.begin() as conn:
            conn.execute(text("""DELETE FROM "tabReport" WHERE name = 'test-sec-query-report'"""))


@patch("internal.core.security.get_security_settings")
def test_server_scripts_blocked(mock_get_sec):
    mock_get_sec.return_value = {
        "developer_mode": True,
        "allow_server_scripts": False,
        "allow_query_reports": True,
        "allow_script_reports": False,
    }
    errors = run_scripts("DocType", "before_save", {"name": "test"})
    assert errors == []


@patch("internal.core.report_engine.get_security_settings")
def test_query_report_allowed_by_default(mock_sec):
    mock_sec.return_value = {
        "developer_mode": True,
        "allow_server_scripts": True,
        "allow_query_reports": True,
        "allow_script_reports": False,
    }
    engine = _get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO "tabReport" (name, ref_doctype, report_type, query, enabled, idx)
                VALUES ('test-sec-query-allowed', 'DocType', 'Query Report', 'SELECT 1 AS col', TRUE, 0)
                ON CONFLICT (name) DO NOTHING
            """)
        )
    try:
        result = run_report("test-sec-query-allowed")
        assert result["success"] is True
        assert result["data"] == [{"col": 1}]
    finally:
        with engine.begin() as conn:
            conn.execute(text("""DELETE FROM "tabReport" WHERE name = 'test-sec-query-allowed'"""))

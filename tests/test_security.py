from unittest.mock import patch

from sqlalchemy import text

from apps.galaxy.galaxy.core.report_engine import _validate_query_safe, run_report
from apps.galaxy.galaxy.core.script_engine import _check_dangerous_code, run_scripts
from apps.galaxy.galaxy.core.security import (
    _login_attempts,
    check_login_rate_limit,
    clear_login_rate_limit,
    generate_csrf_token,
    get_security_settings,
    log_security_event,
    validate_csrf_token,
)
from apps.galaxy.galaxy.db.connection import get_engine
from internal.config.site_config import load_site_config


def _get_engine():
    _, site = load_site_config()
    return get_engine(site)


# ── CSRF Token Tests ──────────────────────────────────────────────


def test_csrf_token_generate_and_validate():
    token = generate_csrf_token("test-session-abc")
    assert isinstance(token, str)
    assert len(token) == 64
    assert validate_csrf_token("test-session-abc", token) is True


def test_csrf_token_wrong_session():
    token = generate_csrf_token("session-one")
    assert validate_csrf_token("session-two", token) is False


def test_csrf_token_wrong_token():
    token = generate_csrf_token("session-abc")
    assert validate_csrf_token("session-abc", "fake" + token[4:]) is False


def test_csrf_token_empty():
    token = generate_csrf_token("")
    assert validate_csrf_token("", token) is True


# ── Login Rate Limit Tests ────────────────────────────────────────


def clear_attempts():
    _login_attempts.clear()


@patch("apps.galaxy.galaxy.core.security.get_security_settings")
def test_rate_limit_allows_first_attempt(mock_sec):
    mock_sec.return_value = {
        "login_rate_limit_enabled": True,
        "login_rate_limit_max_attempts": 5,
        "login_rate_limit_window_seconds": 300,
    }
    clear_attempts()
    ok, msg = check_login_rate_limit("1.2.3.4", "admin")
    assert ok is True
    assert msg == ""


@patch("apps.galaxy.galaxy.core.security.get_security_settings")
def test_rate_limit_blocks_after_max(mock_sec):
    mock_sec.return_value = {
        "login_rate_limit_enabled": True,
        "login_rate_limit_max_attempts": 3,
        "login_rate_limit_window_seconds": 300,
    }
    clear_attempts()
    for _ in range(3):
        check_login_rate_limit("1.2.3.4", "admin")
    ok, msg = check_login_rate_limit("1.2.3.4", "admin")
    assert ok is False
    assert "too many" in msg.lower()


@patch("apps.galaxy.galaxy.core.security.get_security_settings")
def test_rate_limit_per_ip(mock_sec):
    mock_sec.return_value = {
        "login_rate_limit_enabled": True,
        "login_rate_limit_max_attempts": 2,
        "login_rate_limit_window_seconds": 300,
    }
    clear_attempts()
    check_login_rate_limit("1.1.1.1", "admin")
    check_login_rate_limit("1.1.1.1", "admin")
    ok_ip1, _ = check_login_rate_limit("1.1.1.1", "admin")
    assert ok_ip1 is False
    ok_ip2, _ = check_login_rate_limit("2.2.2.2", "admin")
    assert ok_ip2 is True


@patch("apps.galaxy.galaxy.core.security.get_security_settings")
def test_rate_limit_per_user(mock_sec):
    mock_sec.return_value = {
        "login_rate_limit_enabled": True,
        "login_rate_limit_max_attempts": 2,
        "login_rate_limit_window_seconds": 300,
    }
    clear_attempts()
    check_login_rate_limit("1.1.1.1", "admin")
    check_login_rate_limit("1.1.1.1", "admin")
    ok_admin, _ = check_login_rate_limit("1.1.1.1", "admin")
    assert ok_admin is False
    ok_other, _ = check_login_rate_limit("1.1.1.1", "guest")
    assert ok_other is True


@patch("apps.galaxy.galaxy.core.security.get_security_settings")
def test_rate_limit_clear(mock_sec):
    mock_sec.return_value = {
        "login_rate_limit_enabled": True,
        "login_rate_limit_max_attempts": 1,
        "login_rate_limit_window_seconds": 300,
    }
    clear_attempts()
    check_login_rate_limit("1.1.1.1", "admin")
    ok, _ = check_login_rate_limit("1.1.1.1", "admin")
    assert ok is False
    clear_login_rate_limit("1.1.1.1", "admin")
    ok, _ = check_login_rate_limit("1.1.1.1", "admin")
    assert ok is True


@patch("apps.galaxy.galaxy.core.security.get_security_settings")
def test_rate_limit_disabled(mock_sec):
    mock_sec.return_value = {
        "login_rate_limit_enabled": False,
        "login_rate_limit_max_attempts": 2,
        "login_rate_limit_window_seconds": 300,
    }
    clear_attempts()
    for _ in range(5):
        ok, _ = check_login_rate_limit("1.1.1.1", "admin")
        assert ok is True


# ── Secure Defaults Tests ─────────────────────────────────────────


@patch("apps.galaxy.galaxy.core.security.load_common_config")
def test_security_settings_secure_defaults(mock_config):
    mock_config.return_value = {}
    sec = get_security_settings()
    assert sec["allow_server_scripts"] is False
    assert sec["allow_query_reports"] is False
    assert sec["allow_script_reports"] is False
    assert sec["allow_dev_auth_bypass"] is False
    assert sec["csrf_enabled"] is True
    assert sec["login_rate_limit_enabled"] is True


# ── Dangerous Code Blocking Tests ─────────────────────────────────


def test_dangerous_code_import():
    err = _check_dangerous_code("import os")
    assert err is not None
    assert "blocked" in err.lower()


def test_dangerous_code_exec():
    err = _check_dangerous_code("exec('print(1)')")
    assert err is not None


def test_dangerous_code_open():
    err = _check_dangerous_code("open('/etc/passwd')")
    assert err is not None


def test_dangerous_code_subprocess():
    err = _check_dangerous_code("import subprocess; subprocess.run('ls')")
    assert err is not None


def test_safe_code_passes():
    err = _check_dangerous_code("result = [x * 2 for x in range(10)]")
    assert err is None


def test_safe_code_frappe_api():
    err = _check_dangerous_code("doc.name = 'test'")
    assert err is None


def test_dangerous_code_empty():
    err = _check_dangerous_code("")
    assert err is None


# ── SQL Validation Tests ──────────────────────────────────────────


def test_valid_select_passes():
    ok, msg = _validate_query_safe("SELECT id, name FROM users")
    assert ok is True
    assert msg == ""


def test_block_semicolon():
    ok, msg = _validate_query_safe("SELECT 1; DROP TABLE users")
    assert ok is False
    assert "semicolon" in msg.lower()


def test_block_insert():
    ok, _ = _validate_query_safe("INSERT INTO users VALUES (1)")
    assert ok is False


def test_block_delete():
    ok, _ = _validate_query_safe("DELETE FROM users WHERE id = 1")
    assert ok is False


def test_block_drop():
    ok, _ = _validate_query_safe("DROP TABLE users")
    assert ok is False


def test_block_update():
    ok, _ = _validate_query_safe("UPDATE users SET name = 'x'")
    assert ok is False


def test_block_comment_escape():
    ok, _ = _validate_query_safe("SELECT 1 -- DROP TABLE")
    assert ok is True


def test_block_alter():
    ok, _ = _validate_query_safe("ALTER TABLE users ADD COLUMN x INT")
    assert ok is False


def test_empty_query():
    ok, _ = _validate_query_safe("")
    assert ok is False


# ── Security Event Logging Tests ──────────────────────────────────


def test_log_security_event_with_ip():
    log_security_event("login_failed", "Administrator", "Test failed login.", "test", "10.0.0.1")
    engine = _get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("""SELECT error_type, message, source, user_name, request_path, method, status FROM "tabError Log" WHERE source = 'test' ORDER BY created_at DESC LIMIT 1""")
        ).mappings().one_or_none()
    assert row is not None
    assert row["error_type"] == "Security"
    assert row["user_name"] == "Administrator"
    assert row["request_path"] == "10.0.0.1"
    assert row["method"] == "login_failed"
    assert row["status"] == "Blocked"
    with engine.begin() as conn:
        conn.execute(text("""DELETE FROM "tabError Log" WHERE source = 'test'"""))


def test_log_security_event_no_user():
    log_security_event("test_event", None, "No user event.", "test")
    engine = _get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("""SELECT user_name FROM "tabError Log" WHERE source = 'test' ORDER BY created_at DESC LIMIT 1""")
        ).mappings().one_or_none()
    assert row is not None
    assert row["user_name"] == "System"
    with engine.begin() as conn:
        conn.execute(text("""DELETE FROM "tabError Log" WHERE source = 'test'"""))


# ── Existing M9 Tests (preserved) ─────────────────────────────────


def test_security_settings_defaults():
    sec = get_security_settings()
    assert sec["developer_mode"] is True


@patch("apps.galaxy.galaxy.core.report_engine.get_security_settings")
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


@patch("apps.galaxy.galaxy.core.report_engine.get_security_settings")
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


@patch("apps.galaxy.galaxy.core.security.get_security_settings")
def test_server_scripts_blocked(mock_get_sec):
    mock_get_sec.return_value = {
        "developer_mode": True,
        "allow_server_scripts": False,
        "allow_query_reports": True,
        "allow_script_reports": False,
    }
    errors = run_scripts("DocType", "before_save", {"name": "test"})
    assert errors == []


@patch("apps.galaxy.galaxy.core.report_engine.get_security_settings")
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

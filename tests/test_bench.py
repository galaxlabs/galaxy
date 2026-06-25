import json
import os
import shutil

import pytest
from galaxy.bench_manager.platform_db import (
    get_connection,
    get_site,
    init_platform_db,
    list_sites,
    register_site,
    remove_site,
    site_exists,
    update_site_status,
)
from galaxy.bench_manager.site_manager import (
    backup_site,
    create_site_config,
    get_site_info,
    get_site_migration_status,
    install_app,
    list_apps,
    list_backups,
    list_managed_sites,
    restore_site,
    uninstall_app,
)

SITES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sites")


def _test_site_config(name: str) -> str:
    return os.path.join(SITES_DIR, name, "site_config.json")


@pytest.fixture(autouse=True)
def _fresh_db():
    init_platform_db()
    conn = get_connection()
    conn.execute("DELETE FROM sites")
    conn.commit()
    conn.close()
    yield


def _make_site_dir(name: str):
    site_dir = os.path.join(SITES_DIR, name)
    os.makedirs(site_dir, exist_ok=True)
    config = {
        "site_name": name,
        "db_type": "postgres",
        "db_host": "127.0.0.1",
        "db_port": 5432,
        "db_name": "galaxy_default",
        "db_user": "galaxy_default_user",
        "db_password": "password",
        "installed_apps": ["core"],
        "installed_modules": ["Core", "Setup", "Security", "Desk", "Workspace", "Navigation"],
    }
    with open(_test_site_config(name), "w") as f:
        json.dump(config, f, indent=2)
    return config


def _remove_site_dir(name: str):
    path = os.path.join(SITES_DIR, name)
    if os.path.exists(path):
        shutil.rmtree(path)


def test_init_platform_db():
    init_platform_db()
    conn = get_connection()
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    table_names = [r["name"] for r in tables]
    assert "sites" in table_names
    assert "bench_config" in table_names


def test_register_and_list_site():
    init_platform_db()
    register_site("testsite.local", "db_testsite", "user_testsite", "sites/testsite.local/site_config.json")
    sites = list_sites()
    names = [s["name"] for s in sites]
    assert "testsite.local" in names


def test_site_exists():
    init_platform_db()
    assert site_exists("nonexistent.local") is False
    register_site("exists.local", "db_exists", "user_exists", "sites/exists.local/site_config.json")
    assert site_exists("exists.local") is True


def test_get_site():
    init_platform_db()
    register_site("gettest.local", "db_gettest", "user_gettest", "sites/gettest.local/site_config.json")
    s = get_site("gettest.local")
    assert s is not None
    assert s["name"] == "gettest.local"
    assert s["db_name"] == "db_gettest"
    assert s["db_user"] == "user_gettest"
    assert s["status"] == "created"


def test_update_site_status():
    init_platform_db()
    register_site("statustest.local", "db_statustest", "user_statustest", "sites/statustest.local/site_config.json")
    update_site_status("statustest.local", "running")
    s = get_site("statustest.local")
    assert s["status"] == "running"


def test_remove_site():
    init_platform_db()
    register_site("removetest.local", "db_removetest", "user_removetest", "sites/removetest.local/site_config.json")
    assert site_exists("removetest.local") is True
    remove_site("removetest.local")
    assert site_exists("removetest.local") is False


def test_create_site_config_creates_file():
    init_platform_db()
    name = "configtest.local"
    config = create_site_config(name)
    assert config["site_name"] == name
    assert config["db_type"] == "postgres"
    assert config["db_name"].startswith("galaxy_configtest")
    assert config["db_user"].startswith("galaxy_configtest")

    config_path = _test_site_config(name)
    assert os.path.exists(config_path)

    os.remove(config_path)
    os.rmdir(os.path.dirname(config_path))


def test_list_managed_sites_empty():
    init_platform_db()
    sites = list_managed_sites()
    assert isinstance(sites, list)


def test_get_site_info_nonexistent():
    init_platform_db()
    s = get_site_info("nope.local")
    assert s is None


def test_list_after_register():
    init_platform_db()
    register_site("alpha.local", "db_a", "user_a", "path_a")
    register_site("beta.local", "db_b", "user_b", "path_b")
    sites = list_managed_sites()
    names = [s["name"] for s in sites]
    assert "alpha.local" in names
    assert "beta.local" in names


def test_install_app_creates_config_entry():
    name = "appinstalltest.local"
    _make_site_dir(name)
    register_site(name, "galaxy_default", "galaxy_default_user", _test_site_config(name))

    install_app(name, "test_app_a")
    with open(_test_site_config(name)) as f:
        config = json.load(f)
    assert "test_app_a" in config["installed_apps"]
    _remove_site_dir(name)


def test_install_app_duplicate_raises():
    name = "appdupetest.local"
    _make_site_dir(name)
    register_site(name, "galaxy_default", "galaxy_default_user", _test_site_config(name))

    install_app(name, "test_app_b")
    with pytest.raises(ValueError, match="already installed"):
        install_app(name, "test_app_b")
    _remove_site_dir(name)


def test_install_app_nonexistent_site_raises():
    with pytest.raises(ValueError, match="not found"):
        install_app("nope.local", "myapp")


def test_list_apps_returns_installed():
    name = "applisttest.local"
    _make_site_dir(name)
    register_site(name, "galaxy_default", "galaxy_default_user", _test_site_config(name))

    install_app(name, "test_app_c")
    apps = list_apps(name)
    names = [a["name"] for a in apps]
    assert "test_app_c" in names
    _remove_site_dir(name)


def test_list_apps_includes_core():
    name = "appcoretest.local"
    _make_site_dir(name)
    register_site(name, "galaxy_default", "galaxy_default_user", _test_site_config(name))

    apps = list_apps(name)
    names = [a["name"] for a in apps]
    assert "core" in names
    _remove_site_dir(name)


def test_uninstall_app_removes_from_config():
    name = "appuninstalltest.local"
    _make_site_dir(name)
    register_site(name, "galaxy_default", "galaxy_default_user", _test_site_config(name))

    install_app(name, "test_app_d")
    uninstall_app(name, "test_app_d")
    with open(_test_site_config(name)) as f:
        config = json.load(f)
    assert "test_app_d" not in config["installed_apps"]
    _remove_site_dir(name)


def test_uninstall_app_not_installed_raises():
    name = "appnotinsttest.local"
    _make_site_dir(name)
    register_site(name, "galaxy_default", "galaxy_default_user", _test_site_config(name))

    with pytest.raises(ValueError, match="not installed"):
        uninstall_app(name, "nope")

    _remove_site_dir(name)


def test_uninstall_app_after_uninstall_list_excludes():
    name = "appremovetest.local"
    _make_site_dir(name)
    register_site(name, "galaxy_default", "galaxy_default_user", _test_site_config(name))

    install_app(name, "test_app_e")
    uninstall_app(name, "test_app_e")
    apps = list_apps(name)
    names = [a["name"] for a in apps]
    assert "test_app_e" not in names
    _remove_site_dir(name)


@pytest.fixture
def _backup_site():
    name = "backuptest.local"
    _make_site_dir(name)
    register_site(name, "galaxy_default", "galaxy_default_user", _test_site_config(name))
    yield name
    _remove_site_dir(name)


def test_backup_nonexistent_site_raises():
    with pytest.raises(ValueError, match="not found"):
        import galaxy.bench_manager.site_manager as sm
        sm.backup_site("nope.local")


def test_backup_creates_backup_file(mocker):
    name = "backupfiletest.local"
    _make_site_dir(name)
    register_site(name, "galaxy_default", "galaxy_default_user", _test_site_config(name))

    mocker.patch("galaxy.bench_manager.site_manager._check_pg_dump")
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.returncode = 0
    mock_run.return_value.stderr = ""
    mock_run.return_value.stdout = ""

    def _fake_getsize(path):
        return 12345

    mocker.patch("os.path.getsize", side_effect=_fake_getsize)

    result = backup_site(name)

    assert result["filename"].endswith(".dump")
    assert result["size"] == 12345
    assert result["path"].endswith(result["filename"])
    _remove_site_dir(name)


def test_backup_pg_dump_failure(mocker):
    name = "backupfailtest.local"
    _make_site_dir(name)
    register_site(name, "galaxy_default", "galaxy_default_user", _test_site_config(name))

    mocker.patch("galaxy.bench_manager.site_manager._check_pg_dump")
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = "pg_dump: error: connection failed"
    mock_run.return_value.stdout = ""

    with pytest.raises(RuntimeError, match="connection failed"):
        backup_site(name)
    _remove_site_dir(name)


def test_list_backups_empty():
    name = "backuplistempty.local"
    _make_site_dir(name)
    register_site(name, "galaxy_default", "galaxy_default_user", _test_site_config(name))

    backups = list_backups(name)
    assert backups == []

    _remove_site_dir(name)


def test_list_backups_after_backup(mocker):
    name = "backuplisttest.local"
    _make_site_dir(name)
    register_site(name, "galaxy_default", "galaxy_default_user", _test_site_config(name))

    backup_dir = os.path.join(SITES_DIR, name, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    dummy_file = os.path.join(backup_dir, f"{name}_20260101_120000.dump")
    with open(dummy_file, "w") as f:
        f.write("test")

    backups = list_backups(name)
    assert len(backups) == 1
    assert backups[0]["filename"].endswith(".dump")
    assert backups[0]["size"] > 0

    _remove_site_dir(name)


def test_restore_nonexistent_site_raises():
    with pytest.raises(ValueError, match="not found"):
        restore_site("nope.local", "/fake/path.dump")


def test_restore_missing_file_raises(mocker):
    name = "restoremissingfile.local"
    _make_site_dir(name)
    register_site(name, "galaxy_default", "galaxy_default_user", _test_site_config(name))

    with pytest.raises(ValueError, match="not found"):
        restore_site(name, "/nonexistent/path.dump")

    _remove_site_dir(name)


def test_restore_success(mocker, _backup_site):
    name = _backup_site
    mocker.patch("galaxy.bench_manager.site_manager._check_pg_restore")

    backup_path = os.path.join(SITES_DIR, name, "backups", "test_restore.dump")
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    with open(backup_path, "w") as f:
        f.write("fake dump content")

    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.returncode = 0
    mock_run.return_value.stderr = ""
    mock_run.return_value.stdout = ""

    restore_site(name, backup_path)

    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "pg_restore" in args[0]
    assert "--dbname" in args


def test_restore_pg_restore_failure(mocker, _backup_site):
    name = _backup_site
    mocker.patch("galaxy.bench_manager.site_manager._check_pg_restore")

    backup_path = os.path.join(SITES_DIR, name, "backups", "test_fail.dump")
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    with open(backup_path, "w") as f:
        f.write("fake dump content")

    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = "pg_restore: error: database does not exist"
    mock_run.return_value.stdout = ""

    with pytest.raises(RuntimeError, match="database does not exist"):
        restore_site(name, backup_path)


def test_migration_status_nonexistent_site_raises():
    with pytest.raises(ValueError, match="not found"):
        get_site_migration_status("nope.local")


def test_migration_status_returns_doctypes():
    name = "migstatustest.local"
    _make_site_dir(name)
    register_site(name, "galaxy_default", "galaxy_default_user", _test_site_config(name))

    results = get_site_migration_status(name)

    assert isinstance(results, list)
    assert len(results) > 0
    for r in results:
        assert "name" in r
        assert "table_name" in r
        assert "migration_status" in r
        assert r["migration_status"] in ("applied", "pending")

    _remove_site_dir(name)


def test_migration_status_has_both_statuses():
    name = "migstatustest2.local"
    _make_site_dir(name)
    register_site(name, "galaxy_default", "galaxy_default_user", _test_site_config(name))

    results = get_site_migration_status(name)
    statuses = {r["migration_status"] for r in results}
    assert "applied" in statuses

    _remove_site_dir(name)

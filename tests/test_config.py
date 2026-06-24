import json
from unittest.mock import patch

import pytest

from internal.config.site_config import load_common_config, load_site_config

COMMON_CONFIG = {
    "default_site": "test.local",
    "server_port": 8080,
    "developer_mode": True,
    "production_mode": False,
    "cloud_mode": False,
}

SITE_CONFIG = {
    "site_name": "test.local",
    "db_type": "postgres",
    "db_host": "127.0.0.1",
    "db_port": 5432,
    "db_name": "galaxy_test",
    "db_user": "galaxy_test_user",
    "db_password": "test_password",
    "installed_apps": ["galaxy_core"],
    "installed_modules": ["Core", "Setup", "Security", "Desk", "Workspace", "Navigation"],
}


@pytest.fixture
def temp_sites(tmp_path):
    sites_dir = tmp_path / "sites"
    sites_dir.mkdir()
    (sites_dir / "test.local").mkdir()

    with open(sites_dir / "common_site_config.json", "w") as f:
        json.dump(COMMON_CONFIG, f)

    with open(sites_dir / "test.local" / "site_config.json", "w") as f:
        json.dump(SITE_CONFIG, f)

    return sites_dir


def test_load_common_config(temp_sites):
    with patch("internal.config.site_config._get_sites_dir", return_value=str(temp_sites)):
        config = load_common_config()
        assert config["default_site"] == "test.local"
        assert config["server_port"] == 8080


def test_load_site_config(temp_sites):
    with patch("internal.config.site_config._get_sites_dir", return_value=str(temp_sites)):
        common, site = load_site_config("test.local")
        assert common["default_site"] == "test.local"
        assert site["db_name"] == "galaxy_test"
        assert site["db_user"] == "galaxy_test_user"
        assert "galaxy_core" in site["installed_apps"]


def test_load_site_config_default_site(temp_sites):
    with patch("internal.config.site_config._get_sites_dir", return_value=str(temp_sites)):
        _, site = load_site_config()
        assert site["site_name"] == "test.local"


def test_common_config_missing(temp_sites):
    nonexistent = temp_sites.parent / "no_config"
    with patch("internal.config.site_config._get_sites_dir", return_value=str(nonexistent)):
        with pytest.raises(FileNotFoundError):
            load_common_config()


def test_site_config_missing(temp_sites):
    with patch("internal.config.site_config._get_sites_dir", return_value=str(temp_sites)):
        with pytest.raises(FileNotFoundError):
            load_site_config("nonexistent.local")

import json
import os


def _get_sites_dir():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "sites")


def load_common_config():
    path = os.path.join(_get_sites_dir(), "common_site_config.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Common site config not found: {path}")
    with open(path) as f:
        return json.load(f)


def load_site_config(site_name=None):
    common = load_common_config()
    if site_name is None:
        site_name = common.get("default_site", "default.local")

    site_config_path = os.path.join(_get_sites_dir(), site_name, "site_config.json")
    if not os.path.exists(site_config_path):
        raise FileNotFoundError(f"Site config not found: {site_config_path}")

    with open(site_config_path) as f:
        site = json.load(f)

    return common, site

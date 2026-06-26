from galaxy.config import load_common_config
from galaxy.app import run_server


def start():
    """Start Galaxy HTTP server."""
    common = load_common_config()
    port = common.get("server_port", 8080)
    run_server(host="127.0.0.1", port=port)

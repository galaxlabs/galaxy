from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def build_connection_string(site_config: dict) -> str:
    return (
        f"postgresql+psycopg://{site_config['db_user']}:{site_config['db_password']}"
        f"@{site_config['db_host']}:{site_config['db_port']}/{site_config['db_name']}"
    )


def get_engine(site_config: dict, connect_timeout: int = 5) -> Engine:
    conn_str = build_connection_string(site_config)
    return create_engine(
        conn_str,
        connect_args={"connect_timeout": connect_timeout},
    )


def test_connection(engine: Engine) -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

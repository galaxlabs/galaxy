from galaxy.db.connection import build_connection_string, get_engine

SITE_CONFIG = {
    "db_type": "postgres",
    "db_host": "127.0.0.1",
    "db_port": 5432,
    "db_name": "galaxy_test",
    "db_user": "galaxy_test_user",
    "db_password": "test_password",
}


def test_build_connection_string():
    conn_str = build_connection_string(SITE_CONFIG)
    assert "postgresql+psycopg://" in conn_str
    assert "galaxy_test_user:test_password" in conn_str
    assert "127.0.0.1:5432/galaxy_test" in conn_str


def test_get_engine():
    engine = get_engine(SITE_CONFIG)
    assert engine.url.database == "galaxy_test"
    assert engine.url.host == "127.0.0.1"
    assert engine.url.port == 5432
    assert engine.url.username == "galaxy_test_user"

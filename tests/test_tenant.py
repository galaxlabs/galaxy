
from galaxy.config import load_site_config
from galaxy.core.tenant import (
    create_tenant,
    current_tenant,
    delete_tenant,
    get_tenant_id,
    get_tenants,
    resolve_tenant,
    update_tenant,
)
from galaxy.db.connection import get_engine


def _engine():
    _, site = load_site_config()
    return get_engine(site)


def test_default_tenant_exists():
    t = resolve_tenant("Default")
    assert t is not None
    assert t["name"] == "Default"
    assert t["status"] == "active"


def test_create_tenant():
    name = "test-tenant-1"
    t = create_tenant(name, display_name="Test Tenant 1", domain="test1.example.com")
    assert t["name"] == name
    assert t["display_name"] == "Test Tenant 1"
    assert t["domain"] == "test1.example.com"
    assert t["status"] == "active"
    delete_tenant(name)


def test_create_tenant_minimal():
    name = "test-tenant-2"
    t = create_tenant(name)
    assert t["name"] == name
    assert t["display_name"] == name
    assert t["domain"] == ""
    delete_tenant(name)


def test_resolve_tenant_by_name():
    create_tenant("resolve-me", display_name="Resolve Me")
    t2 = resolve_tenant("resolve-me")
    assert t2 is not None
    assert t2["display_name"] == "Resolve Me"
    delete_tenant("resolve-me")


def test_get_tenants():
    create_tenant("tenant-a")
    create_tenant("tenant-b")
    tenants = get_tenants()
    names = [t["name"] for t in tenants]
    assert "tenant-a" in names
    assert "tenant-b" in names
    delete_tenant("tenant-a")
    delete_tenant("tenant-b")


def test_update_tenant_display_name():
    create_tenant("update-me")
    updated = update_tenant("update-me", display_name="Updated Name")
    assert updated["display_name"] == "Updated Name"
    delete_tenant("update-me")


def test_update_tenant_domain():
    create_tenant("domain-test")
    updated = update_tenant("domain-test", domain="new.example.com")
    assert updated["domain"] == "new.example.com"
    delete_tenant("domain-test")


def test_update_tenant_status():
    create_tenant("status-test")
    updated = update_tenant("status-test", status="inactive")
    assert updated["status"] == "inactive"
    delete_tenant("status-test")


def test_delete_tenant():
    create_tenant("delete-me")
    assert resolve_tenant("delete-me") is not None
    deleted = delete_tenant("delete-me")
    assert deleted is True
    assert resolve_tenant("delete-me") is None


def test_delete_nonexistent_tenant():
    assert delete_tenant("nonexistent-tenant") is False


def test_current_tenant_default():
    assert current_tenant.get() == "Default"


def test_get_tenant_id_from_header():
    class MockRequest:
        def __init__(self):
            self.headers = {"X-Tenant-ID": "acme", "Host": "localhost"}

    tenant_id = get_tenant_id(MockRequest())
    assert tenant_id == "acme"


def test_get_tenant_id_from_subdomain():
    class MockRequest:
        def __init__(self):
            self.headers = {"Host": "acme.example.com"}

    tenant_id = get_tenant_id(MockRequest())
    assert tenant_id == "acme"


def test_get_tenant_id_default():
    class MockRequest:
        def __init__(self):
            self.headers = {"Host": "localhost"}

    tenant_id = get_tenant_id(MockRequest())
    assert tenant_id == "Default"


def test_create_duplicate_tenant():
    create_tenant("duplicate-test")
    try:
        create_tenant("duplicate-test")
        raise AssertionError("Should have raised exception")
    except Exception:
        pass
    delete_tenant("duplicate-test")


def test_resolve_by_domain():
    create_tenant("domain-resolve", domain="my-domain.com")
    t = resolve_tenant("my-domain.com")
    assert t is not None
    assert t["name"] == "domain-resolve"
    delete_tenant("domain-resolve")

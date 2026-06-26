from galaxy.auth import create_session, get_session
from galaxy.config import load_site_config
from galaxy.model.document import create_document, delete_document, get_document, list_documents
from galaxy.tenant import create_tenant, current_tenant, delete_tenant
from galaxy.database.connection import get_engine
from sqlalchemy import text


def _engine():
    _, site = load_site_config()
    return get_engine(site)


def _cleanup(name: str):
    engine = _engine()
    with engine.begin() as conn:
        conn.execute(text('DELETE FROM "tabReport" WHERE name = :n'), {"n": name})


def _set_tenant(tenant: str) -> str:
    tok = current_tenant.set(tenant)
    return tok


def _reset_tenant(token):
    current_tenant.reset(token)


BASE_RPT = {"ref_doctype": "User", "report_type": "Query Report", "query": "SELECT 1"}


def test_crud_list_isolation():
    tok_a = _set_tenant("IsolationA")
    r1 = create_document("Report", {**BASE_RPT})
    assert r1["success"], f"Create A failed: {r1}"
    nm1 = r1["data"]["name"]

    _set_tenant("IsolationB")
    r2 = create_document("Report", {**BASE_RPT})
    assert r2["success"], f"Create B failed: {r2}"
    nm2 = r2["data"]["name"]

    list_b = list_documents("Report")
    names_b = [d["name"] for d in list_b]
    assert nm1 not in names_b, "Tenant A's report leaked into Tenant B's list"
    assert nm2 in names_b, "Tenant B's report missing from own list"

    _set_tenant("IsolationA")
    list_a = list_documents("Report")
    names_a = [d["name"] for d in list_a]
    assert nm1 in names_a, "Tenant A's report missing from own list"
    assert nm2 not in names_a, "Tenant B's report leaked into Tenant A's list"

    _cleanup(nm1)
    _cleanup(nm2)
    _reset_tenant(tok_a)


def test_crud_get_isolation():
    tok_a = _set_tenant("GetIsolA")
    r = create_document("Report", {**BASE_RPT})
    assert r["success"], f"Create failed: {r}"
    nm = r["data"]["name"]

    _set_tenant("GetIsolB")
    doc = get_document("Report", nm)
    assert doc is None, "Tenant A's report was visible to Tenant B via get"

    _set_tenant("GetIsolA")
    doc = get_document("Report", nm)
    assert doc is not None, "Tenant A's report not visible to itself"

    _cleanup(nm)
    _reset_tenant(tok_a)


def test_crud_update_isolation():
    tok_a = _set_tenant("UpdIsolA")
    r = create_document("Report", {**BASE_RPT})
    assert r["success"], f"Create A failed: {r}"
    nm = r["data"]["name"]

    _set_tenant("UpdIsolB")
    r2 = create_document("Report", {**BASE_RPT})
    assert r2["success"], f"Create B failed: {r2}"
    nm2 = r2["data"]["name"]

    result = create_document("Report", {**BASE_RPT, "name": nm})
    assert not result["success"], "Tenant B should not be able to create with Tenant A's name"
    err = result.get("error", "").lower()
    assert "not found" in err or "already exists" in err

    _reset_tenant(tok_a)
    _cleanup(nm)
    _cleanup(nm2)


def test_crud_delete_isolation():
    tok_a = _set_tenant("DelIsolA")
    r = create_document("Report", {**BASE_RPT})
    assert r["success"], f"Create failed: {r}"
    nm = r["data"]["name"]

    _set_tenant("DelIsolB")
    result = delete_document("Report", nm)
    assert not result["success"], "Tenant B was allowed to delete Tenant A's document"

    _set_tenant("DelIsolA")
    doc = get_document("Report", nm)
    assert doc is not None, "Tenant A's document was deleted despite failed cross-tenant attempt"

    _cleanup(nm)
    _reset_tenant(tok_a)


def test_session_isolation():
    tok_default = _set_tenant("SessIsolA")
    token_a = create_session("Administrator")
    session_a = get_session(token_a)
    assert session_a is not None, "Session not found in own tenant"

    _set_tenant("SessIsolB")
    session_b = get_session(token_a)
    assert session_b is None, "Session leaked across tenants"

    _reset_tenant(tok_default)


def test_tenant_create_isolates_reports():
    import random
    suffix = str(random.randint(1000, 9999))
    ta = f"CRIsolA-{suffix}"
    tb = f"CRIsolB-{suffix}"
    create_tenant(ta)
    create_tenant(tb)

    tok_default = _set_tenant(ta)
    r = create_document("Report", {**BASE_RPT})
    assert r["success"], f"Create A failed: {r}"
    nm = r["data"]["name"]

    _set_tenant(tb)
    r2 = create_document("Report", {**BASE_RPT})
    assert r2["success"], f"Create B failed: {r2}"
    nm2 = r2["data"]["name"]

    assert nm != nm2

    list_a = list_documents("Report")
    list_a_names = [d["name"] for d in list_a]
    assert nm not in list_a_names

    _set_tenant(ta)
    list_a_names = [d["name"] for d in list_documents("Report")]
    assert nm in list_a_names
    assert nm2 not in list_a_names

    _cleanup(nm)
    _cleanup(nm2)
    _reset_tenant(tok_default)
    delete_tenant(ta)
    delete_tenant(tb)

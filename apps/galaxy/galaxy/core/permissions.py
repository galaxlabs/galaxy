from sqlalchemy import text

from apps.galaxy.galaxy.db.connection import get_engine
from internal.config.site_config import load_site_config


def _get_engine():
    _, site = load_site_config()
    return get_engine(site)


def get_user_roles(username: str) -> list[str]:
    if username == "Administrator":
        return ["System Manager"]
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text('SELECT role FROM "tabHas Role" WHERE parent = :name'),
            {"name": username},
        ).mappings().all()
    return [r["role"] for r in rows]


def check_permission(doctype_name: str, role: str, perm_type: str) -> bool:
    if role == "System Manager":
        return True

    perm_type = perm_type.lower()
    if perm_type not in ("read", "write", "create", "delete"):
        return False

    with _get_engine().connect() as conn:
        row = conn.execute(
            text(f"""
                SELECT {perm_type} FROM "tabDocPerm"
                WHERE parent = :parent AND role = :role
                ORDER BY permlevel LIMIT 1
            """),
            {"parent": doctype_name, "role": role},
        ).mappings().one_or_none()

    if row is None:
        return False
    return bool(row[perm_type])


def authorize(doctype_name: str, username: str | None, perm_type: str) -> tuple[bool, str]:
    if not username:
        return False, "Authentication required."

    roles = get_user_roles(username)
    if not roles:
        return False, f"User '{username}' has no roles assigned."

    for role in roles:
        if check_permission(doctype_name, role, perm_type):
            return True, ""

    return False, f"User '{username}' lacks '{perm_type}' permission on '{doctype_name}'."


def user_has_role(username: str, target_role: str) -> bool:
    return target_role in get_user_roles(username)

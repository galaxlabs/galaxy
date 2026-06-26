from galaxy.model.runtimemeta import RuntimeMeta
from galaxy.model.repository import get_runtime_meta
from galaxy.model.permission_engine import (
    apply_field_permissions,
    apply_data_masks,
    check_permission_rule,
    filter_list_by_permission,
    get_field_restrictions,
    get_effective_mask_rules,
)
from galaxy.permissions import get_user_roles


def _get_effective_role(username: str) -> str:
    roles = get_user_roles(username)
    return roles[0] if roles else ""


def enforce_phase4_get(doctype: str, username: str, doc_data: dict | None) -> dict | None:
    if doc_data is None:
        return None
    meta = get_runtime_meta(doctype)
    if meta is None:
        return doc_data
    role = _get_effective_role(username)
    read_fields, _ = get_field_restrictions(meta, role)
    result = apply_field_permissions(doc_data, role, read_fields or [])
    masks = get_effective_mask_rules(meta, role)
    result = apply_data_masks(result, role, masks)
    return result


def enforce_phase4_list(doctype: str, username: str, docs: list[dict]) -> list[dict]:
    if not docs:
        return docs
    meta = get_runtime_meta(doctype)
    if meta is None:
        return docs
    role = _get_effective_role(username)
    perm_rules = meta.permission_rules or []
    filtered = filter_list_by_permission(docs, role, perm_rules, "read")
    read_fields, _ = get_field_restrictions(meta, role)
    masks = get_effective_mask_rules(meta, role)
    result = []
    for d in filtered:
        item = apply_field_permissions(d, role, read_fields or [])
        item = apply_data_masks(item, role, masks)
        result.append(item)
    return result


def enforce_phase4_create(doctype: str, username: str, doc_data: dict) -> bool:
    meta = get_runtime_meta(doctype)
    if meta is None:
        return True
    role = _get_effective_role(username)
    perm_rules = meta.permission_rules or []
    return check_permission_rule(perm_rules, role, doc_data, "create")


def enforce_phase4_update(doctype: str, username: str, doc_data: dict) -> bool:
    meta = get_runtime_meta(doctype)
    if meta is None:
        return True
    role = _get_effective_role(username)
    perm_rules = meta.permission_rules or []
    return check_permission_rule(perm_rules, role, doc_data, "write")


def enforce_phase4_delete(doctype: str, username: str, doc_data: dict) -> bool:
    meta = get_runtime_meta(doctype)
    if meta is None:
        return True
    role = _get_effective_role(username)
    perm_rules = meta.permission_rules or []
    return check_permission_rule(perm_rules, role, doc_data, "delete")


__all__ = [
    "enforce_phase4_get",
    "enforce_phase4_list",
    "enforce_phase4_create",
    "enforce_phase4_update",
    "enforce_phase4_delete",
]

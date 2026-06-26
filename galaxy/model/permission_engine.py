from galaxy.model.field_rule_engine import _safe_eval


def _mask_value(value, mask_type: str, mask_char: str = "*", prefix: int = 0, suffix: int = 0):
    if value is None:
        return None
    s = str(value)
    if mask_type == "full":
        return mask_char * len(s)
    if mask_type == "partial":
        if prefix + suffix >= len(s):
            return mask_char * len(s)
        return s[:prefix] + mask_char * (len(s) - prefix - suffix) + s[-suffix:] if suffix > 0 else s[:prefix] + mask_char * (len(s) - prefix)
    if mask_type == "email":
        parts = s.split("@", 1)
        if len(parts) == 2:
            local = parts[0]
            masked_local = local[0] + mask_char * max(len(local) - 1, 0) if local else mask_char
            return f"{masked_local}@{parts[1]}"
        return mask_char * len(s)
    if mask_type == "phone":
        visible = min(4, len(s))
        return mask_char * (len(s) - visible) + s[-visible:]
    return s


def apply_field_permissions(doc_data: dict, role: str, read_fields: list[str]) -> dict:
    if doc_data is None:
        return None
    if not read_fields:
        return doc_data
    filtered = {}
    for key, val in doc_data.items():
        if key in ("name", "doctype") or key in read_fields:
            filtered[key] = val
    return filtered


def apply_data_masks(doc_data: dict, role: str, mask_rules: list[dict]) -> dict:
    if not mask_rules or doc_data is None:
        return doc_data
    result = dict(doc_data)
    for rule in mask_rules:
        field = rule.get("field_name")
        if field not in doc_data:
            continue
        if rule.get("condition"):
            try:
                if not _safe_eval(rule["condition"], doc_data):
                    continue
            except Exception:
                continue
        result[field] = _mask_value(
            doc_data[field],
            rule.get("mask_type", "full"),
            rule.get("mask_character", "*"),
            rule.get("unmasked_prefix_len", 0),
            rule.get("unmasked_suffix_len", 0),
        )
    return result


def check_permission_rule(perm_rules: list[dict], role: str, doc_data: dict, perm_type: str) -> bool:
    if not perm_rules:
        return True
    for rule in perm_rules:
        if rule.get("role") != role:
            continue
        if not rule.get("enabled", True):
            continue
        if not rule.get(perm_type, False):
            continue
        condition = rule.get("condition")
        if condition:
            try:
                if not _safe_eval(condition, doc_data):
                    return False
            except Exception:
                return False
        return True
    return True


def filter_list_by_permission(docs: list[dict], role: str, perm_rules: list[dict], perm_type: str) -> list[dict]:
    if not perm_rules:
        return docs
    return [d for d in docs if check_permission_rule(perm_rules, role, d, perm_type)]


def get_field_restrictions(meta, role: str) -> tuple[list[str] | None, list[str]]:
    field_perms = [fp for fp in (meta.field_permissions or []) if not fp.get("enabled", True) is False]
    role_perms = [fp for fp in field_perms if fp.get("role") == role]
    if not role_perms:
        return None, []
    read_fields = [fp["field_name"] for fp in role_perms if fp.get("read")]
    write_fields = [fp["field_name"] for fp in role_perms if fp.get("write")]
    return read_fields if read_fields else None, write_fields


def get_effective_mask_rules(meta, role: str) -> list[dict]:
    rules = meta.data_mask_rules or []
    role_rules = [r for r in rules if not r.get("role") or r["role"] == role]
    return [r for r in role_rules if r.get("enabled", True)]


__all__ = [
    "apply_field_permissions",
    "apply_data_masks",
    "check_permission_rule",
    "filter_list_by_permission",
    "get_field_restrictions",
    "get_effective_mask_rules",
]

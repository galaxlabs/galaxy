from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuntimeMeta:
    doctype: dict[str, Any]
    fields: list[dict[str, Any]] = field(default_factory=list)
    field_map: dict[str, dict[str, Any]] = field(default_factory=dict)
    permissions: list[dict[str, Any]] = field(default_factory=list)
    custom_fields: list[dict[str, Any]] = field(default_factory=list)
    property_setters: list[dict[str, Any]] = field(default_factory=list)
    settings: dict[str, Any] = field(default_factory=dict)
    field_rules: list[dict[str, Any]] = field(default_factory=list)
    field_rules_map: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    field_dependencies: list[dict[str, Any]] = field(default_factory=list)
    field_deps_map: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    computed_fields: list[dict[str, Any]] = field(default_factory=list)
    field_permissions: list[dict[str, Any]] = field(default_factory=list)
    field_perms_map: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    data_mask_rules: list[dict[str, Any]] = field(default_factory=list)
    data_mask_map: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    permission_rules: list[dict[str, Any]] = field(default_factory=list)
    display_logic: list[dict[str, Any]] = field(default_factory=list)
    display_logic_map: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    dynamic_sources: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

    def get_field(self, fieldname: str) -> dict[str, Any] | None:
        return self.field_map.get(fieldname)

    def get_title_field(self) -> str:
        return self.settings.get("title_field") or self.fields[0]["fieldname"] if self.fields else "name"

    def get_search_fields(self) -> list[str]:
        raw = self.settings.get("search_fields", "")
        if raw:
            return [f.strip() for f in raw.split("\n") if f.strip()]
        return [self.get_title_field()]

    def get_sort_field(self) -> str:
        return self.settings.get("sort_field") or "name"

    def get_sort_order(self) -> str:
        return self.settings.get("sort_order") or "ASC"

    def get_icon(self) -> str:
        return self.settings.get("icon") or "FileText"

    def get_icon_provider(self) -> str:
        return self.settings.get("icon_provider") or "lucide"

    def get_field_rules(self, fieldname: str) -> list[dict[str, Any]]:
        return self.field_rules_map.get(fieldname, [])

    def get_field_dependencies(self, fieldname: str) -> list[dict[str, Any]]:
        return self.field_deps_map.get(fieldname, [])

    def get_computed_field(self, fieldname: str) -> dict[str, Any] | None:
        for cf in self.computed_fields:
            if cf["field_name"] == fieldname:
                return cf
        return None

    def get_field_permissions(self, fieldname: str) -> list[dict[str, Any]]:
        return self.field_perms_map.get(fieldname, [])

    def get_data_mask_rules(self, fieldname: str) -> list[dict[str, Any]]:
        return self.data_mask_map.get(fieldname, [])

    def get_permission_rules(self, role: str | None = None) -> list[dict[str, Any]]:
        if role is None:
            return self.permission_rules
        return [pr for pr in self.permission_rules if pr["role"] == role]

    def can_read_field(self, fieldname: str, role: str) -> bool:
        perms = self.field_perms_map.get(fieldname, [])
        if not perms:
            return True
        return any(p["role"] == role and p.get("read", False) for p in perms)

    def can_write_field(self, fieldname: str, role: str) -> bool:
        perms = self.field_perms_map.get(fieldname, [])
        if not perms:
            return True
        return any(p["role"] == role and p.get("write", False) for p in perms)


def _apply_property_setter(field: dict, psetter: dict) -> dict:
    prop = psetter["property"]
    val = psetter["value"]
    field = dict(field)
    if prop == "reqd":
        field["reqd"] = val in ("1", "true", "True", True)
    elif prop == "hidden":
        field["hidden"] = val in ("1", "true", "True", True)
    elif prop == "read_only":
        field["read_only"] = val in ("1", "true", "True", True)
    elif prop == "in_list_view":
        field["in_list_view"] = val in ("1", "true", "True", True)
    elif prop == "label":
        field["label"] = str(val)
    elif prop == "fieldtype":
        field["fieldtype"] = str(val)
    elif prop == "options":
        field["options"] = str(val)
    elif prop == "default":
        field["default"] = str(val)
    elif prop == "description":
        field["description"] = str(val)
    elif prop in field:
        ftype = field.get("fieldtype", "Data")
        if ftype in ("Check", "Int"):
            try:
                field[prop] = int(val)
            except (ValueError, TypeError):
                field[prop] = val
        else:
            field[prop] = str(val)
    return field


def _apply_doctype_property_setter(doctype: dict, psetter: dict) -> dict:
    prop = psetter["property"]
    val = psetter["value"]
    doctype = dict(doctype)
    if prop in ("is_submittable", "is_child_table", "is_tree", "is_single"):
        doctype[prop] = val in ("1", "true", "True", True)
    elif prop in doctype:
        doctype[prop] = val
    return doctype


def _build_field_index_map(items: list[dict], key: str = "field_name") -> dict[str, list[dict]]:
    idx: dict[str, list[dict]] = {}
    for item in items:
        fname = item.get(key)
        if fname:
            idx.setdefault(fname, []).append(dict(item))
    return idx


def merge_meta(
    doctype: dict[str, Any] | None,
    base_fields: list[dict[str, Any]],
    permissions: list[dict[str, Any]],
    custom_fields: list[dict[str, Any]] | None = None,
    property_setters: list[dict[str, Any]] | None = None,
    settings: dict[str, Any] | None = None,
    field_rules: list[dict[str, Any]] | None = None,
    field_dependencies: list[dict[str, Any]] | None = None,
    computed_fields: list[dict[str, Any]] | None = None,
    field_permissions: list[dict[str, Any]] | None = None,
    data_mask_rules: list[dict[str, Any]] | None = None,
    permission_rules: list[dict[str, Any]] | None = None,
    display_logic: list[dict[str, Any]] | None = None,
    dynamic_sources: list[dict[str, Any]] | None = None,
) -> RuntimeMeta | None:
    if doctype is None:
        return None

    fields: list[dict[str, Any]] = [dict(f) for f in base_fields]
    field_map: dict[str, int] = {f["fieldname"]: i for i, f in enumerate(fields)}

    cf_list = custom_fields or []
    for cf in cf_list:
        fields.append(dict(cf))
        field_map[cf["fieldname"]] = len(fields) - 1

    ps_list = property_setters or []
    global_ps: list[dict] = []
    for ps in ps_list:
        fname = ps.get("field_name")
        if "enabled" in ps and not ps["enabled"]:
            continue
        if fname:
            idx = field_map.get(fname)
            if idx is not None:
                fields[idx] = _apply_property_setter(fields[idx], ps)
        else:
            global_ps.append(ps)

    merged_doctype = dict(doctype)
    for ps in global_ps:
        merged_doctype = _apply_doctype_property_setter(merged_doctype, ps)

    final_field_map: dict[str, dict] = {}
    for f in fields:
        final_field_map[f["fieldname"]] = f

    rule_list = [dict(r) for r in (field_rules or [])]
    dep_list = [dict(d) for d in (field_dependencies or [])]
    cf_list_final = [dict(c) for c in (computed_fields or [])]
    fp_list = [dict(p) for p in (field_permissions or [])]
    dm_list = [dict(r) for r in (data_mask_rules or [])]
    pr_list = [dict(r) for r in (permission_rules or [])]
    dl_list = [dict(d) for d in (display_logic or [])]
    ds_list = [dict(s) for s in (dynamic_sources or [])]

    ds_map: dict[str, list[dict]] = {}
    for s in ds_list:
        fname = s.get("field_name", "")
        if fname:
            ds_map.setdefault(fname, []).append(s)

    return RuntimeMeta(
        doctype=merged_doctype,
        fields=fields,
        field_map=final_field_map,
        permissions=[dict(p) for p in permissions],
        custom_fields=[dict(cf) for cf in cf_list],
        property_setters=[dict(ps) for ps in ps_list],
        settings=dict(settings or {}),
        field_rules=rule_list,
        field_rules_map=_build_field_index_map(rule_list),
        field_dependencies=dep_list,
        field_deps_map=_build_field_index_map(dep_list),
        computed_fields=cf_list_final,
        field_permissions=fp_list,
        field_perms_map=_build_field_index_map(fp_list),
        data_mask_rules=dm_list,
        data_mask_map=_build_field_index_map(dm_list),
        permission_rules=pr_list,
        display_logic=dl_list,
        display_logic_map=_build_field_index_map(dl_list),
        dynamic_sources=ds_map,
    )

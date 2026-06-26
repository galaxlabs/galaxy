from galaxy.model.field_type_registry import get_all_types, options_required
from galaxy.model.document import RESERVED_FIELD_NAMES

VALID_FIELDTYPES = set(get_all_types().keys())
OPTIONS_REQUIRED = {name for name, td in get_all_types().items() if td.options_required}

RESERVED_FIELD_NAMES = {
    "name", "owner", "creation", "modified", "modified_by",
    "idx", "parent", "parentfield", "parenttype", "doctype",
    "docstatus", "_user_tags", "_comments", "_assign",
    "_liked_by", "__islocal", "__onload", "__run_trigger",
    "tenant_id", "created_at", "updated_at",
}

DEFAULT_DOCTYPE_FIELDS = {
    "is_single": False,
    "is_submittable": False,
    "is_child_table": False,
    "is_tree": False,
}

DEFAULT_FIELD_FIELDS = {
    "reqd": False,
    "hidden": False,
    "read_only": False,
    "in_list_view": False,
}


def validate_doctype_payload(payload: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    required_dt = ["name", "module", "label", "table_name"]
    for field in required_dt:
        val = payload.get(field)
        if not val or not isinstance(val, str) or not val.strip():
            errors.append(f"DocType field '{field}' is required and must be a non-empty string.")

    fields = payload.get("fields")
    if not fields or not isinstance(fields, list):
        errors.append("'fields' must be a non-empty array.")
        return errors, warnings

    if len(fields) == 0:
        errors.append("'fields' array must contain at least one field.")
        return errors, warnings

    for i, f in enumerate(fields):
        prefix = f"fields[{i}]"
        fname = f.get("fieldname")
        flabel = f.get("label")
        ftype = f.get("fieldtype")

        if not fname or not isinstance(fname, str) or not fname.strip():
            errors.append(f"{prefix}: 'fieldname' is required and must be a non-empty string.")
        elif fname.strip() in RESERVED_FIELD_NAMES:
            errors.append(f"{prefix}: fieldname '{fname}' is reserved and cannot be used.")
        if not flabel or not isinstance(flabel, str) or not flabel.strip():
            errors.append(f"{prefix}: 'label' is required and must be a non-empty string.")
        if not ftype or not isinstance(ftype, str) or not ftype.strip():
            errors.append(f"{prefix}: 'fieldtype' is required and must be a non-empty string.")
        elif ftype not in VALID_FIELDTYPES:
            errors.append(f"{prefix}: unsupported fieldtype '{ftype}'. Valid types: {', '.join(sorted(VALID_FIELDTYPES))}.")
        elif ftype in OPTIONS_REQUIRED:
            opts = f.get("options")
            if not opts or not isinstance(opts, str) or not opts.strip():
                errors.append(f"{prefix}: 'options' is required for fieldtype '{ftype}'.")

        if ftype == "Table" and fname:
            target = f.get("options", "")
            if target and target == payload.get("name"):
                warnings.append(f"{prefix}: Table field '{fname}' points to its own DocType (self-reference).")

    name = payload.get("name", "")
    table = payload.get("table_name", "")
    if name and table and not table.startswith("tab"):
        warnings.append("Convention: 'table_name' should start with 'tab' (e.g. 'tab" + name + "').")

    return errors, warnings


def build_doctype_json(payload: dict) -> dict:
    name = payload["name"].strip()
    module = payload.get("module", "Core").strip()
    app_name = payload.get("app_name", "core").strip()
    table_name = payload.get("table_name", f"tab{name}").strip()
    is_single = payload.get("is_single", DEFAULT_DOCTYPE_FIELDS["is_single"])
    is_submittable = payload.get("is_submittable", DEFAULT_DOCTYPE_FIELDS["is_submittable"])
    is_child_table = payload.get("is_child_table", DEFAULT_DOCTYPE_FIELDS["is_child_table"])
    is_tree = payload.get("is_tree", DEFAULT_DOCTYPE_FIELDS["is_tree"])

    doctype = {
        "name": name,
        "module": module,
        "app_name": app_name,
        "table_name": table_name,
        "is_single": bool(is_single),
        "is_submittable": bool(is_submittable),
        "is_child_table": bool(is_child_table),
        "is_tree": bool(is_tree),
        "idx": 0,
    }

    raw_fields = payload.get("fields", [])
    fields = []

    for idx, f in enumerate(raw_fields):
        fieldname = f.get("fieldname", "").strip()
        label = f.get("label", "").strip()
        fieldtype = f.get("fieldtype", "Data").strip()
        options = f.get("options")
        if options is not None:
            options = options.strip()
            if options == "":
                options = None

        field = {
            "name": f"{name}.{fieldname}",
            "parent": name,
            "fieldname": fieldname,
            "label": label,
            "fieldtype": fieldtype,
            "options": options,
            "reqd": bool(f.get("reqd", DEFAULT_FIELD_FIELDS["reqd"])),
            "hidden": bool(f.get("hidden", DEFAULT_FIELD_FIELDS["hidden"])),
            "read_only": bool(f.get("read_only", DEFAULT_FIELD_FIELDS["read_only"])),
            "in_list_view": bool(f.get("in_list_view", DEFAULT_FIELD_FIELDS["in_list_view"])),
            "idx": idx,
        }
        fields.append(field)

    return {"doctype": doctype, "fields": fields}

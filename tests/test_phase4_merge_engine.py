from galaxy.core.doctype.runtimemeta import RuntimeMeta, merge_meta


SAMPLE_DOCTYPE = {
    "name": "Employee",
    "module": "Core",
    "app_name": "core",
    "table_name": "tabEmployee",
    "is_single": False,
    "is_submittable": False,
    "is_child_table": False,
    "is_tree": False,
    "idx": 0,
    "migration_status": "applied",
}

SAMPLE_FIELDS = [
    {"fieldname": "employee_name", "label": "Employee Name", "fieldtype": "Data", "reqd": True, "idx": 0},
    {"fieldname": "salary", "label": "Salary", "fieldtype": "Float", "reqd": False, "idx": 1},
    {"fieldname": "email", "label": "Email", "fieldtype": "Data", "reqd": False, "idx": 2},
    {"fieldname": "phone", "label": "Phone", "fieldtype": "Data", "reqd": False, "idx": 3},
]

SAMPLE_PERMS = [
    {"role": "System Manager", "permlevel": 0, "read": True, "write": True, "create": True, "delete": True, "idx": 0},
]


def test_merge_meta_with_field_permissions():
    perms = [
        {"field_name": "salary", "role": "HR Manager", "read": True, "write": True, "enabled": True, "idx": 0},
        {"field_name": "salary", "role": "Employee", "read": False, "write": False, "enabled": True, "idx": 1},
    ]
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS, field_permissions=perms)
    assert meta is not None
    assert len(meta.field_permissions) == 2
    assert len(meta.get_field_permissions("salary")) == 2
    assert len(meta.get_field_permissions("email")) == 0
    assert meta.can_read_field("salary", "HR Manager") is True
    assert meta.can_write_field("salary", "HR Manager") is True
    assert meta.can_read_field("salary", "Employee") is False


def test_field_permissions_no_restrictions():
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS)
    assert meta is not None
    assert meta.can_read_field("salary", "Anyone") is True
    assert meta.can_write_field("salary", "Anyone") is True


def test_merge_meta_with_data_mask_rules():
    rules = [
        {"field_name": "email", "mask_type": "email", "mask_character": "*", "enabled": True, "idx": 0},
        {"field_name": "phone", "mask_type": "partial", "mask_character": "*", "unmasked_prefix_len": 3, "unmasked_suffix_len": 2, "enabled": True, "idx": 1},
    ]
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS, data_mask_rules=rules)
    assert meta is not None
    assert len(meta.data_mask_rules) == 2
    assert len(meta.get_data_mask_rules("email")) == 1
    assert len(meta.get_data_mask_rules("phone")) == 1
    assert len(meta.get_data_mask_rules("salary")) == 0
    assert meta.get_data_mask_rules("email")[0]["mask_type"] == "email"


def test_merge_meta_with_permission_rules():
    rules = [
        {"role": "HR Manager", "read": True, "write": True, "create": True, "delete": False, "condition": "doc.department == 'HR'", "enabled": True, "idx": 0},
        {"role": "Manager", "read": True, "write": True, "create": False, "delete": False, "condition": "doc.department == doc.owner_department", "enabled": True, "idx": 1},
    ]
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS, permission_rules=rules)
    assert meta is not None
    assert len(meta.permission_rules) == 2
    rules_for_hr = meta.get_permission_rules("HR Manager")
    assert len(rules_for_hr) == 1
    assert rules_for_hr[0]["delete"] is False
    all_rules = meta.get_permission_rules()
    assert len(all_rules) == 2


def test_merge_meta_all_phase4_layers():
    fp = [{"field_name": "salary", "role": "HR Manager", "read": True, "write": True, "enabled": True, "idx": 0}]
    dm = [{"field_name": "email", "mask_type": "email", "mask_character": "*", "enabled": True, "idx": 0}]
    pr = [{"role": "HR Manager", "read": True, "write": True, "create": True, "delete": False, "enabled": True, "idx": 0}]
    meta = merge_meta(
        SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS,
        field_permissions=fp, data_mask_rules=dm, permission_rules=pr,
    )
    assert meta is not None
    assert len(meta.field_permissions) == 1
    assert len(meta.data_mask_rules) == 1
    assert len(meta.permission_rules) == 1
    assert meta.can_read_field("salary", "HR Manager") is True


def test_runtimemeta_get_field_permissions_empty():
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS)
    assert meta is not None
    assert meta.get_field_permissions("email") == []


def test_runtimemeta_get_data_mask_rules_empty():
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS)
    assert meta is not None
    assert meta.get_data_mask_rules("email") == []


def test_runtimemeta_get_permission_rules_empty():
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS)
    assert meta is not None
    assert meta.get_permission_rules() == []
    assert meta.get_permission_rules("AnyRole") == []

from galaxy.core.doctype.runtimemeta import RuntimeMeta, merge_meta


SAMPLE_DOCTYPE = {
    "name": "Invoice",
    "module": "Accounting",
    "app_name": "erp",
    "table_name": "tabInvoice",
    "is_single": False,
    "is_submittable": True,
    "is_child_table": False,
    "is_tree": False,
    "idx": 0,
    "migration_status": "applied",
}

SAMPLE_FIELDS = [
    {"fieldname": "customer", "label": "Customer", "fieldtype": "Data", "reqd": True, "hidden": False, "read_only": False, "in_list_view": True, "idx": 0},
    {"fieldname": "amount", "label": "Amount", "fieldtype": "Float", "reqd": True, "hidden": False, "read_only": False, "in_list_view": True, "idx": 1},
    {"fieldname": "status", "label": "Status", "fieldtype": "Select", "options": "Draft\nSubmitted\nCancelled", "reqd": True, "hidden": False, "read_only": False, "in_list_view": True, "idx": 2},
    {"fieldname": "discount", "label": "Discount", "fieldtype": "Float", "reqd": False, "hidden": False, "read_only": False, "in_list_view": False, "idx": 3},
]

SAMPLE_PERMS = [
    {"role": "System Manager", "permlevel": 0, "read": True, "write": True, "create": True, "delete": True, "idx": 0},
]


def test_merge_meta_with_field_rules():
    rules = [
        {"field_name": "amount", "rule_type": "min_value", "value": "0", "enabled": True, "idx": 0},
        {"field_name": "amount", "rule_type": "max_value", "value": "999999", "enabled": True, "idx": 1},
        {"field_name": "discount", "rule_type": "mandatory_if", "condition": "doc.amount > 1000", "enabled": True, "idx": 2},
    ]
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS, field_rules=rules)
    assert meta is not None
    assert len(meta.field_rules) == 3
    assert len(meta.get_field_rules("amount")) == 2
    assert len(meta.get_field_rules("discount")) == 1
    assert len(meta.get_field_rules("customer")) == 0


def test_merge_meta_field_rules_disabled_still_included():
    rules = [
        {"field_name": "amount", "rule_type": "min_value", "value": "0", "enabled": False, "idx": 0},
    ]
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS, field_rules=rules)
    assert meta is not None
    assert len(meta.field_rules) == 1
    assert meta.field_rules[0]["enabled"] is False


def test_merge_meta_with_field_dependencies():
    deps = [
        {"field_name": "discount", "depends_on_field": "status", "depends_on_value": "Submitted", "action": "show", "enabled": True, "idx": 0},
    ]
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS, field_dependencies=deps)
    assert meta is not None
    assert len(meta.field_dependencies) == 1
    assert len(meta.get_field_dependencies("discount")) == 1
    dep = meta.get_field_dependencies("discount")[0]
    assert dep["depends_on_field"] == "status"
    assert dep["action"] == "show"


def test_merge_meta_with_computed_fields():
    computed = [
        {"field_name": "total", "formula": "doc.amount - doc.discount", "fieldtype": "Float", "script_type": "Expression", "enabled": True, "idx": 0},
    ]
    # total is a computed field, so it shouldn't be in base_fields
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS, computed_fields=computed)
    assert meta is not None
    assert len(meta.computed_fields) == 1
    assert meta.get_computed_field("total") is not None
    assert meta.get_computed_field("total")["formula"] == "doc.amount - doc.discount"
    assert meta.get_computed_field("nonexistent") is None


def test_merge_meta_all_phase3_layers():
    rules = [
        {"field_name": "amount", "rule_type": "min_value", "value": "0", "enabled": True, "idx": 0},
    ]
    deps = [
        {"field_name": "discount", "depends_on_field": "status", "depends_on_value": "Submitted", "action": "show", "enabled": True, "idx": 0},
    ]
    computed = [
        {"field_name": "total", "formula": "amount - discount", "fieldtype": "Float", "script_type": "Expression", "enabled": True, "idx": 0},
    ]
    meta = merge_meta(
        SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS,
        field_rules=rules,
        field_dependencies=deps,
        computed_fields=computed,
    )
    assert meta is not None
    assert len(meta.field_rules) == 1
    assert len(meta.field_dependencies) == 1
    assert len(meta.computed_fields) == 1
    assert meta.doctype["name"] == "Invoice"
    assert len(meta.fields) == 4


def test_runtimemeta_get_field_rules_empty():
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS)
    assert meta is not None
    assert meta.get_field_rules("amount") == []
    assert meta.get_field_rules("nonexistent") == []


def test_runtimemeta_get_field_dependencies_empty():
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS)
    assert meta is not None
    assert meta.get_field_dependencies("amount") == []


def test_runtimemeta_get_computed_field_none():
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS)
    assert meta is not None
    assert meta.get_computed_field("any") is None

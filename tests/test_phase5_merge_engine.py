from galaxy.model.runtimemeta import merge_meta


DT = {"name": "Invoice", "module": "Accounting", "app_name": "erp",
      "table_name": "tabInvoice", "is_single": False, "is_submittable": True,
      "is_child_table": False, "is_tree": False, "idx": 0, "migration_status": "applied"}
FIELDS = [
    {"fieldname": "amount", "label": "Amount", "fieldtype": "Float", "reqd": True, "hidden": False, "read_only": False, "in_list_view": True, "idx": 0},
    {"fieldname": "status", "label": "Status", "fieldtype": "Select", "options": "Draft\nSubmitted\nCancelled", "reqd": True, "hidden": False, "read_only": False, "in_list_view": True, "idx": 1},
    {"fieldname": "discount", "label": "Discount", "fieldtype": "Float", "reqd": False, "hidden": False, "read_only": False, "in_list_view": False, "idx": 2},
]
PERMS = [{"role": "System Manager", "permlevel": 0, "read": True, "write": True, "create": True, "delete": True, "idx": 0}]


def test_merge_meta_with_display_logic():
    logic = [
        {"field_name": "discount", "depends_on_field": "status", "operator": "=", "value": "Submitted", "action": "show", "enabled": True, "idx": 0},
    ]
    meta = merge_meta(DT, FIELDS, PERMS, display_logic=logic)
    assert meta is not None
    assert len(meta.display_logic) == 1
    assert meta.display_logic[0]["field_name"] == "discount"
    assert meta.display_logic[0]["action"] == "show"


def test_merge_meta_with_dynamic_sources():
    sources = [
        {"field_name": "status", "source_type": "static", "source_handler": "", "enabled": True, "idx": 0},
    ]
    meta = merge_meta(DT, FIELDS, PERMS, dynamic_sources=sources)
    assert meta is not None
    assert "status" in meta.dynamic_sources
    assert len(meta.dynamic_sources["status"]) == 1


def test_merge_meta_display_logic_map():
    logic = [
        {"field_name": "discount", "depends_on_field": "status", "operator": "=", "value": "Submitted", "action": "show", "enabled": True, "idx": 0},
        {"field_name": "discount", "depends_on_field": "amount", "operator": ">", "value": "1000", "action": "require", "enabled": True, "idx": 1},
    ]
    meta = merge_meta(DT, FIELDS, PERMS, display_logic=logic)
    assert meta is not None
    assert "discount" in meta.display_logic_map
    assert len(meta.display_logic_map["discount"]) == 2


def test_merge_meta_no_layers():
    meta = merge_meta(DT, FIELDS, PERMS)
    assert meta is not None
    assert meta.display_logic == []
    assert meta.display_logic_map == {}
    assert meta.dynamic_sources == {}


def test_merge_meta_display_logic_disabled_excluded():
    logic = [
        {"field_name": "discount", "depends_on_field": "status", "operator": "=", "value": "Submitted", "action": "show", "enabled": False, "idx": 0},
    ]
    meta = merge_meta(DT, FIELDS, PERMS, display_logic=logic)
    assert meta is not None
    assert len(meta.display_logic) == 1
    assert meta.display_logic[0]["enabled"] is False

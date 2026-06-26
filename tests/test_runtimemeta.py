from galaxy.model.runtimemeta import RuntimeMeta, merge_meta


SAMPLE_DOCTYPE = {
    "name": "TestDoc",
    "module": "Core",
    "app_name": "core",
    "table_name": "tabTestDoc",
    "is_single": False,
    "is_submittable": False,
    "is_child_table": False,
    "is_tree": False,
    "idx": 0,
    "migration_status": "applied",
}

SAMPLE_FIELDS = [
    {"fieldname": "title", "label": "Title", "fieldtype": "Data", "reqd": True, "hidden": False, "read_only": False, "in_list_view": True, "idx": 0},
    {"fieldname": "description", "label": "Description", "fieldtype": "Text", "reqd": False, "hidden": False, "read_only": False, "in_list_view": False, "idx": 1},
    {"fieldname": "amount", "label": "Amount", "fieldtype": "Float", "reqd": False, "hidden": False, "read_only": False, "in_list_view": True, "idx": 2},
]

SAMPLE_PERMS = [
    {"role": "System Manager", "permlevel": 0, "read": True, "write": True, "create": True, "delete": True, "idx": 0},
]


def test_merge_meta_basic():
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS)
    assert meta is not None
    assert meta.doctype["name"] == "TestDoc"
    assert len(meta.fields) == 3
    assert "title" in meta.field_map
    assert meta.get_field("title") is not None
    assert meta.get_field("title")["label"] == "Title"


def test_merge_meta_none_doctype():
    assert merge_meta(None, [], []) is None


def test_merge_meta_custom_fields():
    custom_fields = [
        {"fieldname": "cf_notes", "label": "Custom Notes", "fieldtype": "Text", "reqd": False, "hidden": False, "read_only": False, "in_list_view": False, "idx": 3},
    ]
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS, custom_fields=custom_fields)
    assert meta is not None
    assert len(meta.fields) == 4
    assert meta.get_field("cf_notes") is not None
    assert meta.get_field("cf_notes")["label"] == "Custom Notes"
    assert len(meta.custom_fields) == 1


def test_merge_meta_property_setter_label_override():
    property_setters = [
        {"property": "label", "value": "New Title", "field_name": "title", "enabled": True, "idx": 0},
    ]
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS, property_setters=property_setters)
    assert meta is not None
    assert meta.get_field("title")["label"] == "New Title"
    assert len(meta.property_setters) == 1


def test_merge_meta_property_setter_hidden():
    property_setters = [
        {"property": "hidden", "value": "1", "field_name": "description", "enabled": True, "idx": 0},
    ]
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS, property_setters=property_setters)
    assert meta is not None
    assert meta.get_field("description")["hidden"] is True


def test_merge_meta_property_setter_disabled():
    property_setters = [
        {"property": "label", "value": "Should Not Apply", "field_name": "title", "enabled": False, "idx": 0},
    ]
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS, property_setters=property_setters)
    assert meta is not None
    assert meta.get_field("title")["label"] == "Title"


def test_merge_meta_global_property_setter():
    property_setters = [
        {"property": "is_submittable", "value": "true", "field_name": None, "enabled": True, "idx": 0},
    ]
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS, property_setters=property_setters)
    assert meta is not None
    assert meta.doctype["is_submittable"] is True


def test_merge_meta_settings():
    settings = {
        "icon": "Users",
        "icon_provider": "lucide",
        "title_field": "title",
        "sort_field": "title",
        "sort_order": "ASC",
        "search_fields": "title\ndescription",
    }
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS, settings=settings)
    assert meta is not None
    assert meta.get_icon() == "Users"
    assert meta.get_title_field() == "title"
    assert meta.get_sort_field() == "title"
    assert meta.get_sort_order() == "ASC"
    assert "description" in meta.get_search_fields()


def test_runtime_meta_dataclass():
    meta = RuntimeMeta(
        doctype=SAMPLE_DOCTYPE,
        fields=SAMPLE_FIELDS,
        field_map={f["fieldname"]: f for f in SAMPLE_FIELDS},
        permissions=SAMPLE_PERMS,
        settings={"title_field": "title"},
    )
    assert meta.get_field("amount") is not None
    assert meta.get_field("nonexistent") is None
    assert meta.get_title_field() == "title"
    assert meta.get_icon() == "FileText"


def test_merge_meta_field_count():
    custom_fields = [
        {"fieldname": "cf_a", "label": "A", "fieldtype": "Data", "idx": 3},
        {"fieldname": "cf_b", "label": "B", "fieldtype": "Data", "idx": 4},
    ]
    property_setters = [
        {"property": "reqd", "value": "1", "field_name": "title", "enabled": True, "idx": 0},
    ]
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS, custom_fields=custom_fields, property_setters=property_setters)
    assert meta is not None
    assert len(meta.fields) == 5
    assert meta.fields[0]["reqd"] is True


def test_merge_meta_permissions():
    meta = merge_meta(SAMPLE_DOCTYPE, SAMPLE_FIELDS, SAMPLE_PERMS)
    assert meta is not None
    assert len(meta.permissions) == 1
    assert meta.permissions[0]["role"] == "System Manager"

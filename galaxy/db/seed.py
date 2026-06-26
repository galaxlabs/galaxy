from passlib.hash import bcrypt as passlib_bcrypt
from sqlalchemy import text
from sqlalchemy.engine import Engine


def seed_tenant(engine: Engine) -> None:
    with engine.begin() as conn:
        result = conn.execute(
            text("""SELECT COUNT(*) FROM "tabTenant" WHERE name = :name"""),
            {"name": "Default"},
        )
        if result.scalar() == 0:
            conn.execute(
                text("""
                    INSERT INTO "tabTenant" (name, display_name, domain, status, idx)
                    VALUES (:name, :display_name, :domain, :status, :idx)
                """),
                {
                    "name": "Default",
                    "display_name": "Default Tenant",
                    "domain": "",
                    "status": "active",
                    "idx": 0,
                },
            )


def seed_installed_app(engine: Engine) -> None:
    with engine.begin() as conn:
        result = conn.execute(
            text("""SELECT COUNT(*) FROM "tabInstalled App" WHERE name = :name"""),
            {"name": "core"},
        )
        if result.scalar() == 0:
            conn.execute(
                text("""
                    INSERT INTO "tabInstalled App" (name, app_name, app_version, enabled, idx)
                    VALUES (:name, :app_name, :app_version, :enabled, :idx)
                """),
                {
                    "name": "core",
                    "app_name": "core",
                    "app_version": "0.0.1",
                    "enabled": True,
                    "idx": 0,
                },
            )


def seed_modules(engine: Engine) -> None:
    modules = [
        ("Core", "Core", "core", "Core", "Core system module", 0),
        ("Setup", "Setup", "core", "Setup", "Setup and configuration module", 1),
        ("Security", "Security", "core", "Security", "Security and access control module", 2),
        ("Desk", "Desk", "core", "Desk", "Desk UI module", 3),
        ("Workspace", "Workspace", "core", "Workspace", "Workspace management module", 4),
        ("Navigation", "Navigation", "core", "Navigation", "Navigation module", 5),
    ]

    with engine.begin() as conn:
        for mod in modules:
            result = conn.execute(
                text("""SELECT COUNT(*) FROM "tabInstalled Module" WHERE name = :name"""),
                {"name": mod[0]},
            )
            if result.scalar() == 0:
                conn.execute(
                    text("""
                        INSERT INTO "tabInstalled Module" (name, module_name, app_name, enabled, idx)
                        VALUES (:name, :module_name, :app_name, :enabled, :idx)
                    """),
                    {
                        "name": mod[0],
                        "module_name": mod[0],
                        "app_name": mod[2],
                        "enabled": True,
                        "idx": mod[5],
                    },
                )

            result = conn.execute(
                text("""SELECT COUNT(*) FROM "tabModule Def" WHERE name = :name"""),
                {"name": mod[0]},
            )
            if result.scalar() == 0:
                conn.execute(
                    text("""
                        INSERT INTO "tabModule Def" (name, module_name, app_name, label, description, enabled, idx)
                        VALUES (:name, :module_name, :app_name, :label, :description, :enabled, :idx)
                    """),
                    {
                        "name": mod[0],
                        "module_name": mod[0],
                        "app_name": mod[2],
                        "label": mod[3],
                        "description": mod[4],
                        "enabled": True,
                        "idx": mod[5],
                    },
                )


def seed_roles(engine: Engine) -> None:
    with engine.begin() as conn:
        result = conn.execute(
            text("""SELECT COUNT(*) FROM "tabRole" WHERE name = :name"""),
            {"name": "System Manager"},
        )
        if result.scalar() == 0:
            conn.execute(
                text("""
                    INSERT INTO "tabRole" (name, role_name)
                    VALUES (:name, :role_name)
                """),
                {"name": "System Manager", "role_name": "System Manager"},
            )


def seed_administrator(engine: Engine) -> None:
    password_hash = passlib_bcrypt.hash("admin")

    with engine.begin() as conn:
        result = conn.execute(
            text("""SELECT COUNT(*) FROM "tabUser" WHERE name = :name"""),
            {"name": "Administrator"},
        )
        if result.scalar() == 0:
            conn.execute(
                text("""
                    INSERT INTO "tabUser" (name, username, email, password_hash, enabled, tenant_id)
                    VALUES (:name, :username, :email, :password_hash, :enabled, :tenant_id)
                """),
                {
                    "name": "Administrator",
                    "username": "Administrator",
                    "email": "administrator@galaxy.local",
                    "password_hash": password_hash,
                    "enabled": True,
                    "tenant_id": "Default",
                },
            )

        result = conn.execute(
            text("""SELECT COUNT(*) FROM "tabHas Role" WHERE name = :name"""),
            {"name": "Administrator"},
        )
        if result.scalar() == 0:
            conn.execute(
                text("""
                    INSERT INTO "tabHas Role" (name, parent, role, tenant_id, idx)
                    VALUES (:name, :parent, :role, :tenant_id, :idx)
                """),
                {
                    "name": "Administrator",
                    "parent": "Administrator",
                    "role": "System Manager",
                    "tenant_id": "Default",
                    "idx": 0,
                },
            )


DOCTYPES = [
    ("Installed App", "Setup", "core", "tabInstalled App", False, False, False, False, 0),
    ("Installed Module", "Setup", "core", "tabInstalled Module", False, False, False, False, 1),
    ("Module Def", "Core", "core", "tabModule Def", False, False, False, False, 2),
    ("DocType", "Core", "core", "tabDocType", False, False, False, False, 3),
    ("DocField", "Core", "core", "tabDocField", False, False, False, False, 4),
    ("DocPerm", "Core", "core", "tabDocPerm", False, False, False, False, 5),
    ("User", "Security", "core", "tabUser", False, False, False, False, 6),
    ("Role", "Security", "core", "tabRole", False, False, False, False, 7),
    ("Has Role", "Security", "core", "tabHas Role", False, False, False, False, 8),
    ("Error Log", "Core", "core", "tabError Log", False, False, False, False, 9),
    ("Server Script", "Core", "core", "tabServer Script", False, False, False, False, 10),
    ("Report", "Core", "core", "tabReport", False, False, False, False, 11),
    ("Session", "Security", "core", "tabSession", False, False, False, False, 12),
]


def seed_doctypes(engine: Engine) -> None:
    with engine.begin() as conn:
        for dt in DOCTYPES:
            result = conn.execute(
                text("""SELECT COUNT(*) FROM "tabDocType" WHERE name = :name"""),
                {"name": dt[0]},
            )
            if result.scalar() == 0:
                conn.execute(
                    text("""
                        INSERT INTO "tabDocType"
                        (name, module, app_name, table_name, is_single, is_submittable, is_child_table, is_tree, idx)
                        VALUES (:name, :module, :app_name, :table_name, :is_single, :is_submittable, :is_child_table, :is_tree, :idx)
                    """),
                    {
                        "name": dt[0],
                        "module": dt[1],
                        "app_name": dt[2],
                        "table_name": dt[3],
                        "is_single": dt[4],
                        "is_submittable": dt[5],
                        "is_child_table": dt[6],
                        "is_tree": dt[7],
                        "idx": dt[8],
                    },
                )


DOCFIELDS = {
    "Installed App": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("app_name", "App Name", "Data", None, True, False, False, True, 1),
        ("app_version", "App Version", "Data", None, True, False, False, True, 2),
        ("installed_at", "Installed At", "Datetime", None, False, False, False, False, 3),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 4),
        ("idx", "Idx", "Int", None, False, False, False, False, 5),
    ],
    "Installed Module": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("module_name", "Module Name", "Data", None, True, False, False, True, 1),
        ("app_name", "App Name", "Data", None, True, False, False, True, 2),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 3),
        ("idx", "Idx", "Int", None, False, False, False, False, 4),
    ],
    "Module Def": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("module_name", "Module Name", "Data", None, True, False, False, True, 1),
        ("app_name", "App Name", "Data", None, True, False, False, True, 2),
        ("label", "Label", "Data", None, False, False, False, True, 3),
        ("description", "Description", "Text", None, False, False, False, False, 4),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 5),
        ("idx", "Idx", "Int", None, False, False, False, False, 6),
    ],
    "DocType": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("module", "Module", "Link", "Module Def", False, False, False, True, 1),
        ("app_name", "App Name", "Data", None, True, False, False, True, 2),
        ("table_name", "Table Name", "Data", None, True, False, False, True, 3),
        ("is_single", "Is Single", "Check", None, False, False, False, False, 4),
        ("is_submittable", "Is Submittable", "Check", None, False, False, False, False, 5),
        ("is_child_table", "Is Child Table", "Check", None, False, False, False, False, 6),
        ("is_tree", "Is Tree", "Check", None, False, False, False, False, 7),
        ("idx", "Idx", "Int", None, False, False, False, False, 8),
    ],
    "DocField": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("parent", "Parent", "Data", None, True, False, False, True, 1),
        ("fieldname", "Fieldname", "Data", None, True, False, False, True, 2),
        ("label", "Label", "Data", None, False, False, False, True, 3),
        ("fieldtype", "Fieldtype", "Select", None, True, False, False, True, 4),
        ("options", "Options", "Text", None, False, False, False, False, 5),
        ("reqd", "Mandatory", "Check", None, False, False, False, True, 6),
        ("hidden", "Hidden", "Check", None, False, False, False, False, 7),
        ("read_only", "Read Only", "Check", None, False, False, False, False, 8),
        ("in_list_view", "In List View", "Check", None, False, False, False, True, 9),
        ("idx", "Idx", "Int", None, False, False, False, False, 10),
    ],
    "DocPerm": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("parent", "Parent", "Data", None, True, False, False, True, 1),
        ("role", "Role", "Link", "Role", True, False, False, True, 2),
        ("permlevel", "Permission Level", "Int", None, False, False, False, False, 3),
        ("read", "Read", "Check", None, True, False, False, True, 4),
        ("write", "Write", "Check", None, True, False, False, True, 5),
        ("create", "Create", "Check", None, True, False, False, True, 6),
        ("delete", "Delete", "Check", None, True, False, False, True, 7),
        ("idx", "Idx", "Int", None, False, False, False, False, 8),
    ],
    "User": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("username", "Username", "Data", None, True, False, False, True, 1),
        ("email", "Email", "Data", None, False, False, False, True, 2),
        ("password_hash", "Password Hash", "Data", None, True, False, True, False, 3),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 4),
        ("idx", "Idx", "Int", None, False, False, False, False, 5),
    ],
    "Role": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("role_name", "Role Name", "Data", None, True, False, False, True, 1),
        ("idx", "Idx", "Int", None, False, False, False, False, 2),
    ],
    "Has Role": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("parent", "Parent", "Data", None, True, False, False, True, 1),
        ("role", "Role", "Link", "Role", True, False, False, True, 2),
        ("idx", "Idx", "Int", None, False, False, False, False, 3),
    ],
    "Report": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("module", "Module", "Link", "Module Def", False, False, False, True, 1),
        ("ref_doctype", "Reference DocType", "Link", "DocType", True, False, False, True, 2),
        ("report_type", "Report Type", "Select", "Query Report\nScript Report", True, False, False, True, 3),
        ("query", "Query", "Code", None, False, False, False, False, 4),
        ("script", "Script", "Code", None, False, False, False, False, 5),
        ("columns", "Columns", "JSON", None, False, False, False, False, 6),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 7),
        ("idx", "Idx", "Int", None, False, False, False, False, 8),
    ],
    "Server Script": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("module", "Module", "Link", "Module Def", False, False, False, True, 1),
        ("ref_doctype", "Reference DocType", "Link", "DocType", True, False, False, True, 2),
        ("doctype_event", "DocType Event", "Select", "before_save\nafter_save\nbefore_delete\nafter_delete\non_load", True, False, False, True, 3),
        ("script_type", "Script Type", "Select", "Python", True, False, False, True, 4),
        ("script", "Script", "Code", None, True, False, False, False, 5),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 6),
        ("idx", "Idx", "Int", None, False, False, False, False, 7),
    ],
    "Error Log": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("error_type", "Error Type", "Data", None, False, False, False, True, 1),
        ("message", "Message", "Text", None, False, False, False, True, 2),
        ("stack_trace", "Stack Trace", "Code", None, False, False, False, False, 3),
        ("source", "Source", "Data", None, False, False, False, False, 4),
        ("request_path", "Request Path", "Data", None, False, False, False, False, 5),
        ("method", "Method", "Data", None, False, False, False, False, 6),
        ("user_name", "User", "Data", None, False, False, False, False, 7),
        ("status", "Status", "Data", None, False, False, False, False, 8),
        ("idx", "Idx", "Int", None, False, False, False, False, 9),
    ],
    "Session": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("user_name", "User Name", "Data", None, True, False, False, True, 1),
        ("token", "Token", "Data", None, True, False, False, False, 2),
        ("expires_at", "Expires At", "Datetime", None, True, False, False, False, 3),
        ("idx", "Idx", "Int", None, False, False, False, False, 4),
    ],
}


def seed_docfields(engine: Engine) -> None:
    with engine.begin() as conn:
        for parent, fields in DOCFIELDS.items():
            for (fieldname, label, fieldtype, options, reqd, hidden, read_only, in_list_view, idx) in fields:
                docfield_name = f"{parent}.{fieldname}"
                result = conn.execute(
                    text("""SELECT COUNT(*) FROM "tabDocField" WHERE name = :name"""),
                    {"name": docfield_name},
                )
                if result.scalar() == 0:
                    conn.execute(
                        text("""
                            INSERT INTO "tabDocField"
                            (name, parent, fieldname, label, fieldtype, options, reqd, hidden, read_only, in_list_view, idx)
                            VALUES (:name, :parent, :fieldname, :label, :fieldtype, :options, :reqd, :hidden, :read_only, :in_list_view, :idx)
                        """),
                        {
                            "name": docfield_name,
                            "parent": parent,
                            "fieldname": fieldname,
                            "label": label,
                            "fieldtype": fieldtype,
                            "options": options,
                            "reqd": reqd,
                            "hidden": hidden,
                            "read_only": read_only,
                            "in_list_view": in_list_view,
                            "idx": idx,
                        },
                    )


def seed_docperms(engine: Engine) -> None:
    doctype_names = [
        "Installed App", "Installed Module", "Module Def", "DocType", "DocField",
        "DocPerm", "User", "Role", "Has Role", "Error Log", "Server Script", "Report", "Session",
    ]

    with engine.begin() as conn:
        for idx, parent in enumerate(doctype_names):
            perm_name = f"{parent}-System Manager"
            result = conn.execute(
                text("""SELECT COUNT(*) FROM "tabDocPerm" WHERE name = :name"""),
                {"name": perm_name},
            )
            if result.scalar() == 0:
                conn.execute(
                    text("""
                        INSERT INTO "tabDocPerm"
                        (name, parent, role, permlevel, "read", "write", "create", "delete", idx)
                        VALUES (:name, :parent, :role, :permlevel, :read, :write, :create, :delete, :idx)
                    """),
                    {
                        "name": perm_name,
                        "parent": parent,
                        "role": "System Manager",
                        "permlevel": 0,
                        "read": True,
                        "write": True,
                        "create": True,
                        "delete": True,
                        "idx": idx,
                    },
                )


PHASE2_DOCTYPES = [
    "CustomField",
    "PropertySetter",
    "DocTypeSetting",
]


def seed_phase2_doctypes(engine: Engine) -> None:
    phase2 = [
        ("CustomField", "Core", "core", "tabCustomField", False, False, False, False, 13),
        ("PropertySetter", "Core", "core", "tabPropertySetter", False, False, False, False, 14),
        ("DocTypeSetting", "Core", "core", "tabDocTypeSetting", False, False, False, False, 15),
    ]
    with engine.begin() as conn:
        for dt in phase2:
            result = conn.execute(
                text("""SELECT COUNT(*) FROM "tabDocType" WHERE name = :name"""),
                {"name": dt[0]},
            )
            if result.scalar() == 0:
                conn.execute(
                    text("""
                        INSERT INTO "tabDocType"
                        (name, module, app_name, table_name, is_single, is_submittable, is_child_table, is_tree, idx)
                        VALUES (:name, :module, :app_name, :table_name, :is_single, :is_submittable, :is_child_table, :is_tree, :idx)
                    """),
                    {
                        "name": dt[0],
                        "module": dt[1],
                        "app_name": dt[2],
                        "table_name": dt[3],
                        "is_single": dt[4],
                        "is_submittable": dt[5],
                        "is_child_table": dt[6],
                        "is_tree": dt[7],
                        "idx": dt[8],
                    },
                )

    with engine.begin() as conn:
        for parent in PHASE2_DOCTYPES:
            perm_name = f"{parent}-System Manager"
            result = conn.execute(
                text("""SELECT COUNT(*) FROM "tabDocPerm" WHERE name = :name"""),
                {"name": perm_name},
            )
            if result.scalar() == 0:
                conn.execute(
                    text("""
                        INSERT INTO "tabDocPerm"
                        (name, parent, role, permlevel, "read", "write", "create", "delete", idx)
                        VALUES (:name, :parent, :role, :permlevel, :read, :write, :create, :delete, :idx)
                    """),
                    {
                        "name": perm_name,
                        "parent": parent,
                        "role": "System Manager",
                        "permlevel": 0,
                        "read": True,
                        "write": True,
                        "create": True,
                        "delete": True,
                        "idx": 0,
                    },
                )


PHASE2_DOCFIELDS = {
    "CustomField": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("parent", "Parent", "Data", None, True, False, False, True, 1),
        ("fieldname", "Fieldname", "Data", None, True, False, False, True, 2),
        ("label", "Label", "Data", None, False, False, False, True, 3),
        ("fieldtype", "Fieldtype", "Select", None, True, False, False, True, 4),
        ("options", "Options", "Text", None, False, False, False, False, 5),
        ("reqd", "Mandatory", "Check", None, False, False, False, True, 6),
        ("hidden", "Hidden", "Check", None, False, False, False, False, 7),
        ("read_only", "Read Only", "Check", None, False, False, False, False, 8),
        ("in_list_view", "In List View", "Check", None, False, False, False, True, 9),
        ("in_standard_filter", "In Standard Filter", "Check", None, False, False, False, False, 10),
        ("search_index", "Search Index", "Check", None, False, False, False, False, 11),
        ("allow_on_submit", "Allow On Submit", "Check", None, False, False, False, False, 12),
        ("depends_on", "Depends On", "Code", None, False, False, False, False, 13),
        ("mandatory_depends_on", "Mandatory Depends On", "Code", None, False, False, False, False, 14),
        ("read_only_depends_on", "Read Only Depends On", "Code", None, False, False, False, False, 15),
        ("translatable", "Translatable", "Check", None, False, False, False, False, 16),
        ("description", "Description", "Text", None, False, False, False, False, 17),
        ("default", "Default", "Text", None, False, False, False, False, 18),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 19),
        ("idx", "Idx", "Int", None, False, False, False, False, 20),
    ],
    "PropertySetter": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("parent", "Parent", "Data", None, True, False, False, True, 1),
        ("property", "Property", "Data", None, True, False, False, True, 2),
        ("value", "Value", "Text", None, True, False, False, True, 3),
        ("field_name", "Field Name", "Data", None, False, False, False, False, 4),
        ("property_type", "Property Type", "Select", "Text\nCheck\nInt", False, False, False, False, 5),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 6),
        ("idx", "Idx", "Int", None, False, False, False, False, 7),
    ],
    "DocTypeSetting": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("parent", "Parent", "Data", None, True, False, False, True, 1),
        ("icon", "Icon", "Data", None, False, False, False, True, 2),
        ("icon_provider", "Icon Provider", "Select", "lucide\nheroicons\ntabler\nmaterial\nphosphor\nremix", False, False, False, False, 3),
        ("color", "Color", "Data", None, False, False, False, False, 4),
        ("theme", "Theme", "Data", None, False, False, False, False, 5),
        ("default_view", "Default View", "Select", "list\nform\ngantt\nkanban\ncalendar\nimage", False, False, False, False, 6),
        ("max_attachments", "Max Attachments", "Int", None, False, False, False, False, 7),
        ("allow_rename", "Allow Rename", "Check", None, False, False, False, False, 8),
        ("allow_copy", "Allow Copy", "Check", None, False, False, False, False, 9),
        ("track_changes", "Track Changes", "Check", None, False, False, False, False, 10),
        ("track_seen", "Track Seen", "Check", None, False, False, False, False, 11),
        ("queue_documents", "Queue Documents", "Check", None, False, False, False, False, 12),
        ("quick_entry", "Quick Entry", "Check", None, False, False, False, False, 13),
        ("sort_field", "Sort Field", "Data", None, False, False, False, False, 14),
        ("sort_order", "Sort Order", "Select", "ASC\nDESC", False, False, False, False, 15),
        ("search_fields", "Search Fields", "Code", None, False, False, False, False, 16),
        ("title_field", "Title Field", "Data", None, False, False, False, False, 17),
        ("image_field", "Image Field", "Data", None, False, False, False, False, 18),
        ("enable_auto_repeat", "Enable Auto Repeat", "Check", None, False, False, False, False, 19),
        ("document_type_class", "Document Type Class", "Data", None, False, False, False, False, 20),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 21),
        ("idx", "Idx", "Int", None, False, False, False, False, 22),
    ],
}


def seed_phase2_docfields(engine: Engine) -> None:
    with engine.begin() as conn:
        for parent, fields in PHASE2_DOCFIELDS.items():
            for (fieldname, label, fieldtype, options, reqd, hidden, read_only, in_list_view, idx) in fields:
                docfield_name = f"{parent}.{fieldname}"
                result = conn.execute(
                    text("""SELECT COUNT(*) FROM "tabDocField" WHERE name = :name"""),
                    {"name": docfield_name},
                )
                if result.scalar() == 0:
                    conn.execute(
                        text("""
                            INSERT INTO "tabDocField"
                            (name, parent, fieldname, label, fieldtype, options, reqd, hidden, read_only, in_list_view, idx)
                            VALUES (:name, :parent, :fieldname, :label, :fieldtype, :options, :reqd, :hidden, :read_only, :in_list_view, :idx)
                        """),
                        {
                            "name": docfield_name,
                            "parent": parent,
                            "fieldname": fieldname,
                            "label": label,
                            "fieldtype": fieldtype,
                            "options": options,
                            "reqd": reqd,
                            "hidden": hidden,
                            "read_only": read_only,
                            "in_list_view": in_list_view,
                            "idx": idx,
                        },
                    )


PHASE3_DOCTYPES = [
    "FieldRule",
    "FieldDependency",
    "ComputedField",
]


def seed_phase3_doctypes(engine: Engine) -> None:
    phase3 = [
        ("FieldRule", "Core", "core", "tabFieldRule", False, False, False, False, 16),
        ("FieldDependency", "Core", "core", "tabFieldDependency", False, False, False, False, 17),
        ("ComputedField", "Core", "core", "tabComputedField", False, False, False, False, 18),
    ]
    with engine.begin() as conn:
        for dt in phase3:
            result = conn.execute(
                text("""SELECT COUNT(*) FROM "tabDocType" WHERE name = :name"""),
                {"name": dt[0]},
            )
            if result.scalar() == 0:
                conn.execute(
                    text("""
                        INSERT INTO "tabDocType"
                        (name, module, app_name, table_name, is_single, is_submittable, is_child_table, is_tree, idx)
                        VALUES (:name, :module, :app_name, :table_name, :is_single, :is_submittable, :is_child_table, :is_tree, :idx)
                    """),
                    {
                        "name": dt[0],
                        "module": dt[1],
                        "app_name": dt[2],
                        "table_name": dt[3],
                        "is_single": dt[4],
                        "is_submittable": dt[5],
                        "is_child_table": dt[6],
                        "is_tree": dt[7],
                        "idx": dt[8],
                    },
                )

    with engine.begin() as conn:
        for parent in PHASE3_DOCTYPES:
            perm_name = f"{parent}-System Manager"
            result = conn.execute(
                text("""SELECT COUNT(*) FROM "tabDocPerm" WHERE name = :name"""),
                {"name": perm_name},
            )
            if result.scalar() == 0:
                conn.execute(
                    text("""
                        INSERT INTO "tabDocPerm"
                        (name, parent, role, permlevel, "read", "write", "create", "delete", idx)
                        VALUES (:name, :parent, :role, :permlevel, :read, :write, :create, :delete, :idx)
                    """),
                    {
                        "name": perm_name,
                        "parent": parent,
                        "role": "System Manager",
                        "permlevel": 0,
                        "read": True,
                        "write": True,
                        "create": True,
                        "delete": True,
                        "idx": 0,
                    },
                )


PHASE3_DOCFIELDS = {
    "FieldRule": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("parent", "Parent", "Data", None, True, False, False, True, 1),
        ("field_name", "Field Name", "Data", None, True, False, False, True, 2),
        ("rule_type", "Rule Type", "Select", "mandatory_if\nread_only_if\nhidden_if\nmin_value\nmax_value\npattern\ncustom", True, False, False, True, 3),
        ("value", "Value", "Text", None, False, False, False, False, 4),
        ("condition", "Condition", "Code", None, False, False, False, False, 5),
        ("error_message", "Error Message", "Text", None, False, False, False, False, 6),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 7),
        ("idx", "Idx", "Int", None, False, False, False, False, 8),
    ],
    "FieldDependency": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("parent", "Parent", "Data", None, True, False, False, True, 1),
        ("field_name", "Field Name", "Data", None, True, False, False, True, 2),
        ("depends_on_field", "Depends On Field", "Data", None, True, False, False, True, 3),
        ("depends_on_value", "Depends On Value", "Text", None, False, False, False, False, 4),
        ("action", "Action", "Select", "show\nhide\nmandatory\nread_only\ndisable", True, False, False, True, 5),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 6),
        ("idx", "Idx", "Int", None, False, False, False, False, 7),
    ],
    "ComputedField": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("parent", "Parent", "Data", None, True, False, False, True, 1),
        ("field_name", "Field Name", "Data", None, True, False, False, True, 2),
        ("formula", "Formula", "Code", None, True, False, False, False, 3),
        ("fieldtype", "Fieldtype", "Select", None, True, False, False, True, 4),
        ("options", "Options", "Text", None, False, False, False, False, 5),
        ("script_type", "Script Type", "Select", "Python\nExpression", False, False, False, False, 6),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 7),
        ("idx", "Idx", "Int", None, False, False, False, False, 8),
    ],
}


def seed_phase3_docfields(engine: Engine) -> None:
    with engine.begin() as conn:
        for parent, fields in PHASE3_DOCFIELDS.items():
            for (fieldname, label, fieldtype, options, reqd, hidden, read_only, in_list_view, idx) in fields:
                docfield_name = f"{parent}.{fieldname}"
                result = conn.execute(
                    text("""SELECT COUNT(*) FROM "tabDocField" WHERE name = :name"""),
                    {"name": docfield_name},
                )
                if result.scalar() == 0:
                    conn.execute(
                        text("""
                            INSERT INTO "tabDocField"
                            (name, parent, fieldname, label, fieldtype, options, reqd, hidden, read_only, in_list_view, idx)
                            VALUES (:name, :parent, :fieldname, :label, :fieldtype, :options, :reqd, :hidden, :read_only, :in_list_view, :idx)
                        """),
                        {
                            "name": docfield_name,
                            "parent": parent,
                            "fieldname": fieldname,
                            "label": label,
                            "fieldtype": fieldtype,
                            "options": options,
                            "reqd": reqd,
                            "hidden": hidden,
                            "read_only": read_only,
                            "in_list_view": in_list_view,
                            "idx": idx,
                        },
                    )


PHASE4_DOCTYPES = [
    "FieldPermission",
    "DataMaskRule",
    "PermissionRule",
]


def seed_phase4_doctypes(engine: Engine) -> None:
    phase4 = [
        ("FieldPermission", "Core", "core", "tabFieldPermission", False, False, False, False, 19),
        ("DataMaskRule", "Core", "core", "tabDataMaskRule", False, False, False, False, 20),
        ("PermissionRule", "Core", "core", "tabPermissionRule", False, False, False, False, 21),
    ]


PHASE5_DOCTYPES = [
    "DisplayLogic",
    "DynamicFieldSource",
]


def seed_phase5_doctypes(engine: Engine) -> None:
    phase5 = [
        ("DisplayLogic", "Core", "core", "tabDisplayLogic", False, False, False, False, 22),
        ("DynamicFieldSource", "Core", "core", "tabDynamicFieldSource", False, False, False, False, 23),
    ]
    with engine.begin() as conn:
        for dt in phase5:
            result = conn.execute(
                text("""SELECT COUNT(*) FROM "tabDocType" WHERE name = :name"""),
                {"name": dt[0]},
            )
            if result.scalar() == 0:
                conn.execute(
                    text("""
                        INSERT INTO "tabDocType"
                        (name, module, app_name, table_name, is_single, is_submittable, is_child_table, is_tree, idx)
                        VALUES (:name, :module, :app_name, :table_name, :is_single, :is_submittable, :is_child_table, :is_tree, :idx)
                    """),
                    {
                        "name": dt[0],
                        "module": dt[1],
                        "app_name": dt[2],
                        "table_name": dt[3],
                        "is_single": dt[4],
                        "is_submittable": dt[5],
                        "is_child_table": dt[6],
                        "is_tree": dt[7],
                        "idx": dt[8],
                    },
                )

    with engine.begin() as conn:
        for parent in PHASE5_DOCTYPES:
            perm_name = f"{parent}-System Manager"
            result = conn.execute(
                text("""SELECT COUNT(*) FROM "tabDocPerm" WHERE name = :name"""),
                {"name": perm_name},
            )
            if result.scalar() == 0:
                conn.execute(
                    text("""
                        INSERT INTO "tabDocPerm"
                        (name, parent, role, permlevel, "read", "write", "create", "delete", idx)
                        VALUES (:name, :parent, :role, :permlevel, :read, :write, :create, :delete, :idx)
                    """),
                    {
                        "name": perm_name,
                        "parent": parent,
                        "role": "System Manager",
                        "permlevel": 0,
                        "read": True,
                        "write": True,
                        "create": True,
                        "delete": True,
                        "idx": 0,
                    },
                )


PHASE5_DOCFIELDS = {
    "DisplayLogic": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("parent", "Parent", "Data", None, True, False, False, True, 1),
        ("field_name", "Field Name", "Data", None, True, False, False, True, 2),
        ("depends_on_field", "Depends On Field", "Data", None, False, False, False, False, 3),
        ("operator", "Operator", "Select", "=\n!=\nin\nnot in\n>\n<\n>=\n<=\nis_set\nis_not_set", True, False, False, True, 4),
        ("value", "Value", "Text", None, False, False, False, False, 5),
        ("action", "Action", "Select", "show\nhide\nrequire\nreadonly\nfilter_options\nset_default", True, False, False, True, 6),
        ("condition_group", "Condition Group", "Data", None, False, False, False, False, 7),
        ("priority", "Priority", "Int", None, False, False, False, False, 8),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 9),
        ("idx", "Idx", "Int", None, False, False, False, False, 10),
    ],
    "DynamicFieldSource": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("parent", "Parent", "Data", None, True, False, False, True, 1),
        ("field_name", "Field Name", "Data", None, True, False, False, True, 2),
        ("source_type", "Source Type", "Select", "static\nquery\napi\nscript\nintegration\ndocument\nuser_context", True, False, False, True, 3),
        ("source_handler", "Source Handler", "Code", None, False, False, False, False, 4),
        ("filters", "Filters", "JSON", None, False, False, False, False, 5),
        ("depends_on", "Depends On", "JSON", None, False, False, False, False, 6),
        ("cache_ttl", "Cache TTL", "Int", None, False, False, False, False, 7),
        ("permission_required", "Permission Required", "Data", None, False, False, False, False, 8),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 9),
        ("idx", "Idx", "Int", None, False, False, False, False, 10),
    ],
}


def seed_phase5_docfields(engine: Engine) -> None:
    with engine.begin() as conn:
        for parent, fields in PHASE5_DOCFIELDS.items():
            for (fieldname, label, fieldtype, options, reqd, hidden, read_only, in_list_view, idx) in fields:
                docfield_name = f"{parent}.{fieldname}"
                result = conn.execute(
                    text("""SELECT COUNT(*) FROM "tabDocField" WHERE name = :name"""),
                    {"name": docfield_name},
                )
                if result.scalar() == 0:
                    conn.execute(
                        text("""
                            INSERT INTO "tabDocField"
                            (name, parent, fieldname, label, fieldtype, options, reqd, hidden, read_only, in_list_view, idx)
                            VALUES (:name, :parent, :fieldname, :label, :fieldtype, :options, :reqd, :hidden, :read_only, :in_list_view, :idx)
                        """),
                        {
                            "name": docfield_name,
                            "parent": parent,
                            "fieldname": fieldname,
                            "label": label,
                            "fieldtype": fieldtype,
                            "options": options,
                            "reqd": reqd,
                            "hidden": hidden,
                            "read_only": read_only,
                            "in_list_view": in_list_view,
                            "idx": idx,
                        },
                    )

    with engine.begin() as conn:
        for parent in PHASE5_DOCTYPES:
            perm_name = f"{parent}-System Manager"
            result = conn.execute(
                text("""SELECT COUNT(*) FROM "tabDocPerm" WHERE name = :name"""),
                {"name": perm_name},
            )
            if result.scalar() == 0:
                conn.execute(
                    text("""
                        INSERT INTO "tabDocPerm"
                        (name, parent, role, permlevel, "read", "write", "create", "delete", idx)
                        VALUES (:name, :parent, :role, :permlevel, :read, :write, :create, :delete, :idx)
                    """),
                    {
                        "name": perm_name,
                        "parent": parent,
                        "role": "System Manager",
                        "permlevel": 0,
                        "read": True,
                        "write": True,
                        "create": True,
                        "delete": True,
                        "idx": 0,
                    },
                )


PHASE_PORTAL_DOCTYPES = [
    "PortalUser",
    "PortalRole",
    "PortalPermission",
    "PortalSession",
]


def seed_portal_doctypes(engine: Engine) -> None:
    portal_dt = [
        ("PortalUser", "Portal", "core", "tabPortalUser", False, False, False, False, 22),
        ("PortalRole", "Portal", "core", "tabPortalRole", False, False, False, False, 23),
        ("PortalPermission", "Portal", "core", "tabPortalPermission", False, False, False, False, 24),
        ("PortalSession", "Portal", "core", "tabPortalSession", False, False, False, False, 25),
    ]
    with engine.begin() as conn:
        for dt in portal_dt:
            result = conn.execute(
                text("""SELECT COUNT(*) FROM "tabDocType" WHERE name = :name"""),
                {"name": dt[0]},
            )
            if result.scalar() == 0:
                conn.execute(
                    text("""
                        INSERT INTO "tabDocType"
                        (name, module, app_name, table_name, is_single, is_submittable, is_child_table, is_tree, idx)
                        VALUES (:name, :module, :app_name, :table_name, :is_single, :is_submittable, :is_child_table, :is_tree, :idx)
                    """),
                    {
                        "name": dt[0],
                        "module": dt[1],
                        "app_name": dt[2],
                        "table_name": dt[3],
                        "is_single": dt[4],
                        "is_submittable": dt[5],
                        "is_child_table": dt[6],
                        "is_tree": dt[7],
                        "idx": dt[8],
                    },
                )

    with engine.begin() as conn:
        for parent in PHASE_PORTAL_DOCTYPES:
            perm_name = f"{parent}-System Manager"
            result = conn.execute(
                text("""SELECT COUNT(*) FROM "tabDocPerm" WHERE name = :name"""),
                {"name": perm_name},
            )
            if result.scalar() == 0:
                conn.execute(
                    text("""
                        INSERT INTO "tabDocPerm"
                        (name, parent, role, permlevel, "read", "write", "create", "delete", idx)
                        VALUES (:name, :parent, :role, :permlevel, :read, :write, :create, :delete, :idx)
                    """),
                    {
                        "name": perm_name,
                        "parent": parent,
                        "role": "System Manager",
                        "permlevel": 0,
                        "read": True,
                        "write": True,
                        "create": True,
                        "delete": True,
                        "idx": 0,
                    },
                )


def seed_portal_roles(engine: Engine) -> None:
    portal_roles = [
        ("Portal User", "Portal User", "Default portal user role", 0),
        ("Portal Admin", "Portal Admin", "Portal administrator role", 1),
    ]
    with engine.begin() as conn:
        for role in portal_roles:
            result = conn.execute(
                text("""SELECT COUNT(*) FROM "tabPortalRole" WHERE name = :name"""),
                {"name": role[0]},
            )
            if result.scalar() == 0:
                conn.execute(
                    text("""
                        INSERT INTO "tabPortalRole" (name, role_name, description, enabled, idx)
                        VALUES (:name, :role_name, :description, :enabled, :idx)
                    """),
                    {"name": role[0], "role_name": role[0], "description": role[2], "enabled": True, "idx": role[3]},
                )


PHASE_PORTAL_DOCFIELDS = {
    "PortalUser": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("email", "Email", "Data", None, True, False, False, True, 1),
        ("phone", "Phone", "Data", None, False, False, False, False, 2),
        ("display_name", "Display Name", "Data", None, False, False, False, True, 3),
        ("username", "Username", "Data", None, False, False, False, True, 4),
        ("avatar", "Avatar", "Attach Image", None, False, False, False, False, 5),
        ("language", "Language", "Data", None, False, False, False, False, 6),
        ("timezone", "Timezone", "Data", None, False, False, False, False, 7),
        ("portal_role", "Portal Role", "Link", "PortalRole", False, False, False, True, 8),
        ("linked_doctype", "Linked DocType", "Data", None, False, False, False, False, 9),
        ("linked_docname", "Linked Document", "Data", None, False, False, False, False, 10),
        ("account_status", "Account Status", "Select", "active\nsuspended\ndisabled\npending_verification", True, False, False, True, 11),
        ("email_verified", "Email Verified", "Check", None, False, False, False, False, 12),
        ("phone_verified", "Phone Verified", "Check", None, False, False, False, False, 13),
        ("password_hash", "Password Hash", "Data", None, True, False, True, False, 14),
        ("last_login", "Last Login", "Datetime", None, False, False, False, False, 15),
        ("idx", "Idx", "Int", None, False, False, False, False, 16),
    ],
    "PortalRole": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("role_name", "Role Name", "Data", None, True, False, False, True, 1),
        ("description", "Description", "Text", None, False, False, False, False, 2),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 3),
        ("idx", "Idx", "Int", None, False, False, False, False, 4),
    ],
    "PortalPermission": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("parent", "Parent", "Data", None, True, False, False, True, 1),
        ("portal_role", "Portal Role", "Link", "PortalRole", True, False, False, True, 2),
        ("permlevel", "Permission Level", "Int", None, False, False, False, False, 3),
        ("read", "Read", "Check", None, True, False, False, True, 4),
        ("write", "Write", "Check", None, True, False, False, True, 5),
        ("create", "Create", "Check", None, True, False, False, True, 6),
        ("delete", "Delete", "Check", None, True, False, False, True, 7),
        ("comment", "Comment", "Check", None, False, False, False, False, 8),
        ("upload", "Upload", "Check", None, False, False, False, False, 9),
        ("download", "Download", "Check", None, False, False, False, False, 10),
        ("export", "Export", "Check", None, False, False, False, False, 11),
        ("run_action", "Run Action", "Check", None, False, False, False, False, 12),
        ("idx", "Idx", "Int", None, False, False, False, False, 13),
    ],
    "PortalSession": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("user_name", "User Name", "Data", None, True, False, False, True, 1),
        ("token", "Token", "Data", None, True, False, False, False, 2),
        ("expires_at", "Expires At", "Datetime", None, True, False, False, False, 3),
        ("idx", "Idx", "Int", None, False, False, False, False, 4),
    ],
}


def seed_portal_docfields(engine: Engine) -> None:
    with engine.begin() as conn:
        for parent, fields in PHASE_PORTAL_DOCFIELDS.items():
            for (fieldname, label, fieldtype, options, reqd, hidden, read_only, in_list_view, idx) in fields:
                docfield_name = f"{parent}.{fieldname}"
                result = conn.execute(
                    text("""SELECT COUNT(*) FROM "tabDocField" WHERE name = :name"""),
                    {"name": docfield_name},
                )
                if result.scalar() == 0:
                    conn.execute(
                        text("""
                            INSERT INTO "tabDocField"
                            (name, parent, fieldname, label, fieldtype, options, reqd, hidden, read_only, in_list_view, idx)
                            VALUES (:name, :parent, :fieldname, :label, :fieldtype, :options, :reqd, :hidden, :read_only, :in_list_view, :idx)
                        """),
                        {
                            "name": docfield_name,
                            "parent": parent,
                            "fieldname": fieldname,
                            "label": label,
                            "fieldtype": fieldtype,
                            "options": options,
                            "reqd": reqd,
                            "hidden": hidden,
                            "read_only": read_only,
                            "in_list_view": in_list_view,
                            "idx": idx,
                        },
                    )


def seed_portal_module(engine: Engine) -> None:
    with engine.begin() as conn:
        result = conn.execute(
            text("""SELECT COUNT(*) FROM "tabInstalled Module" WHERE name = :name"""),
            {"name": "Portal"},
        )
        if result.scalar() == 0:
            conn.execute(
                text("""
                    INSERT INTO "tabInstalled Module" (name, module_name, app_name, enabled, idx)
                    VALUES (:name, :module_name, :app_name, :enabled, :idx)
                """),
                {"name": "Portal", "module_name": "Portal", "app_name": "core", "enabled": True, "idx": 6},
            )
        result = conn.execute(
            text("""SELECT COUNT(*) FROM "tabModule Def" WHERE name = :name"""),
            {"name": "Portal"},
        )
        if result.scalar() == 0:
            conn.execute(
                text("""
                    INSERT INTO "tabModule Def" (name, module_name, app_name, label, description, enabled, idx)
                    VALUES (:name, :module_name, :app_name, :label, :description, :enabled, :idx)
                """),
                {
                    "name": "Portal",
                    "module_name": "Portal",
                    "app_name": "core",
                    "label": "Portal",
                    "description": "Portal module for external user access",
                    "enabled": True,
                    "idx": 6,
                },
            )


PHASE4_DOCFIELDS = {
    "FieldPermission": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("parent", "Parent", "Data", None, True, False, False, True, 1),
        ("field_name", "Field Name", "Data", None, True, False, False, True, 2),
        ("role", "Role", "Link", "Role", True, False, False, True, 3),
        ("permlevel", "Permission Level", "Int", None, False, False, False, False, 4),
        ("read", "Read", "Check", None, True, False, False, True, 5),
        ("write", "Write", "Check", None, True, False, False, True, 6),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 7),
        ("idx", "Idx", "Int", None, False, False, False, False, 8),
    ],
    "DataMaskRule": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("parent", "Parent", "Data", None, True, False, False, True, 1),
        ("field_name", "Field Name", "Data", None, True, False, False, True, 2),
        ("role", "Role", "Link", "Role", False, False, False, False, 3),
        ("mask_type", "Mask Type", "Select", "full\npartial\nemail\nphone", True, False, False, True, 4),
        ("mask_character", "Mask Character", "Data", None, False, False, False, False, 5),
        ("unmasked_prefix_len", "Unmasked Prefix Length", "Int", None, False, False, False, False, 6),
        ("unmasked_suffix_len", "Unmasked Suffix Length", "Int", None, False, False, False, False, 7),
        ("condition", "Condition", "Code", None, False, False, False, False, 8),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 9),
        ("idx", "Idx", "Int", None, False, False, False, False, 10),
    ],
    "PermissionRule": [
        ("name", "Name", "Data", None, True, False, False, True, 0),
        ("parent", "Parent", "Data", None, True, False, False, True, 1),
        ("role", "Role", "Link", "Role", True, False, False, True, 2),
        ("permlevel", "Permission Level", "Int", None, False, False, False, False, 3),
        ("read", "Read", "Check", None, True, False, False, True, 4),
        ("write", "Write", "Check", None, True, False, False, True, 5),
        ("create", "Create", "Check", None, True, False, False, True, 6),
        ("delete", "Delete", "Check", None, True, False, False, True, 7),
        ("select", "Select", "Check", None, False, False, False, False, 8),
        ("amend", "Amend", "Check", None, False, False, False, False, 9),
        ("condition", "Condition", "Code", None, False, False, False, False, 10),
        ("apply_to_child", "Apply To Child", "Check", None, False, False, False, False, 11),
        ("enabled", "Enabled", "Check", None, False, False, False, True, 12),
        ("idx", "Idx", "Int", None, False, False, False, False, 13),
    ],
}


def seed_phase4_docfields(engine: Engine) -> None:
    with engine.begin() as conn:
        for parent, fields in PHASE4_DOCFIELDS.items():
            for (fieldname, label, fieldtype, options, reqd, hidden, read_only, in_list_view, idx) in fields:
                docfield_name = f"{parent}.{fieldname}"
                result = conn.execute(
                    text("""SELECT COUNT(*) FROM "tabDocField" WHERE name = :name"""),
                    {"name": docfield_name},
                )
                if result.scalar() == 0:
                    conn.execute(
                        text("""
                            INSERT INTO "tabDocField"
                            (name, parent, fieldname, label, fieldtype, options, reqd, hidden, read_only, in_list_view, idx)
                            VALUES (:name, :parent, :fieldname, :label, :fieldtype, :options, :reqd, :hidden, :read_only, :in_list_view, :idx)
                        """),
                        {
                            "name": docfield_name,
                            "parent": parent,
                            "fieldname": fieldname,
                            "label": label,
                            "fieldtype": fieldtype,
                            "options": options,
                            "reqd": reqd,
                            "hidden": hidden,
                            "read_only": read_only,
                            "in_list_view": in_list_view,
                            "idx": idx,
                        },
                    )

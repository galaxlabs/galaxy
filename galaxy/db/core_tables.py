from sqlalchemy import text
from sqlalchemy.engine import Engine

TENANT_COL = 'tenant_id VARCHAR(255) NOT NULL DEFAULT \'Default\''

TENANT_TABLES = {
    "tabUser",
    "tabSession",
    "tabHas Role",
    "tabServer Script",
    "tabReport",
    "tabError Log",
    "tabTenant",
}


def _tenant_alter(table: str) -> str:
    return f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255) NOT NULL DEFAULT \'Default\';'


def create_core_tables(engine: Engine) -> None:
    statements = [
        """
        CREATE TABLE IF NOT EXISTS "tabInstalled App" (
            name VARCHAR(255) PRIMARY KEY,
            app_name VARCHAR(255) NOT NULL,
            app_version VARCHAR(50) NOT NULL DEFAULT '0.0.1',
            installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            enabled BOOLEAN DEFAULT TRUE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabInstalled Module" (
            name VARCHAR(255) PRIMARY KEY,
            module_name VARCHAR(255) NOT NULL,
            app_name VARCHAR(255) NOT NULL,
            enabled BOOLEAN DEFAULT TRUE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabModule Def" (
            name VARCHAR(255) PRIMARY KEY,
            module_name VARCHAR(255) NOT NULL,
            app_name VARCHAR(255) NOT NULL,
            label VARCHAR(255),
            description TEXT,
            enabled BOOLEAN DEFAULT TRUE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabDocType" (
            name VARCHAR(255) PRIMARY KEY,
            module VARCHAR(255),
            app_name VARCHAR(255),
            table_name VARCHAR(255),
            is_single BOOLEAN DEFAULT FALSE,
            is_submittable BOOLEAN DEFAULT FALSE,
            is_child_table BOOLEAN DEFAULT FALSE,
            is_tree BOOLEAN DEFAULT FALSE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabDocField" (
            name VARCHAR(255) PRIMARY KEY,
            parent VARCHAR(255) NOT NULL,
            fieldname VARCHAR(255) NOT NULL,
            label VARCHAR(255),
            fieldtype VARCHAR(100) DEFAULT 'Data',
            options TEXT,
            reqd BOOLEAN DEFAULT FALSE,
            hidden BOOLEAN DEFAULT FALSE,
            read_only BOOLEAN DEFAULT FALSE,
            in_list_view BOOLEAN DEFAULT FALSE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabDocPerm" (
            name VARCHAR(255) PRIMARY KEY,
            parent VARCHAR(255) NOT NULL,
            role VARCHAR(255) NOT NULL,
            permlevel INTEGER DEFAULT 0,
            "read" BOOLEAN DEFAULT TRUE,
            "write" BOOLEAN DEFAULT TRUE,
            "create" BOOLEAN DEFAULT TRUE,
            "delete" BOOLEAN DEFAULT TRUE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabUser" (
            name VARCHAR(255) PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            email VARCHAR(255),
            password_hash VARCHAR(255) NOT NULL,
            enabled BOOLEAN DEFAULT TRUE,
            tenant_id VARCHAR(255) NOT NULL DEFAULT 'Default',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabRole" (
            name VARCHAR(255) PRIMARY KEY,
            role_name VARCHAR(255) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabHas Role" (
            name VARCHAR(255) PRIMARY KEY,
            parent VARCHAR(255) NOT NULL,
            role VARCHAR(255) NOT NULL,
            tenant_id VARCHAR(255) NOT NULL DEFAULT 'Default',
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabReport" (
            name VARCHAR(255) PRIMARY KEY,
            module VARCHAR(255),
            ref_doctype VARCHAR(255) NOT NULL,
            report_type VARCHAR(50) NOT NULL DEFAULT 'Query Report',
            query TEXT,
            script TEXT,
            columns JSONB,
            enabled BOOLEAN DEFAULT TRUE,
            tenant_id VARCHAR(255) NOT NULL DEFAULT 'Default',
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabServer Script" (
            name VARCHAR(255) PRIMARY KEY,
            module VARCHAR(255),
            ref_doctype VARCHAR(255) NOT NULL,
            doctype_event VARCHAR(50) NOT NULL,
            script_type VARCHAR(20) DEFAULT 'Python',
            script TEXT,
            enabled BOOLEAN DEFAULT TRUE,
            tenant_id VARCHAR(255) NOT NULL DEFAULT 'Default',
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabError Log" (
            name VARCHAR(255) PRIMARY KEY,
            error_type VARCHAR(255),
            message TEXT,
            stack_trace TEXT,
            source VARCHAR(255),
            request_path VARCHAR(255),
            method VARCHAR(255),
            user_name VARCHAR(255),
            status VARCHAR(50),
            tenant_id VARCHAR(255) NOT NULL DEFAULT 'Default',
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabSession" (
            name VARCHAR(255) PRIMARY KEY,
            user_name VARCHAR(255) NOT NULL,
            token VARCHAR(255) NOT NULL UNIQUE,
            tenant_id VARCHAR(255) NOT NULL DEFAULT 'Default',
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabTenant" (
            name VARCHAR(255) PRIMARY KEY,
            display_name VARCHAR(255) NOT NULL,
            domain VARCHAR(255),
            status VARCHAR(50) NOT NULL DEFAULT 'active',
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    ]

    phase2_statements = [
        """
        CREATE TABLE IF NOT EXISTS "tabCustomField" (
            name VARCHAR(255) PRIMARY KEY,
            parent VARCHAR(255) NOT NULL,
            fieldname VARCHAR(255) NOT NULL,
            label VARCHAR(255),
            fieldtype VARCHAR(100) DEFAULT 'Data',
            options TEXT,
            reqd BOOLEAN DEFAULT FALSE,
            hidden BOOLEAN DEFAULT FALSE,
            read_only BOOLEAN DEFAULT FALSE,
            in_list_view BOOLEAN DEFAULT FALSE,
            in_standard_filter BOOLEAN DEFAULT FALSE,
            search_index BOOLEAN DEFAULT FALSE,
            allow_on_submit BOOLEAN DEFAULT FALSE,
            depends_on TEXT,
            mandatory_depends_on TEXT,
            read_only_depends_on TEXT,
            translatable BOOLEAN DEFAULT FALSE,
            description TEXT,
            "default" TEXT,
            enabled BOOLEAN DEFAULT TRUE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabPropertySetter" (
            name VARCHAR(255) PRIMARY KEY,
            parent VARCHAR(255) NOT NULL,
            property VARCHAR(255) NOT NULL,
            value TEXT,
            field_name VARCHAR(255),
            property_type VARCHAR(50) DEFAULT 'Text',
            enabled BOOLEAN DEFAULT TRUE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabDocTypeSetting" (
            name VARCHAR(255) PRIMARY KEY,
            parent VARCHAR(255) NOT NULL,
            icon VARCHAR(255),
            icon_provider VARCHAR(50) DEFAULT 'lucide',
            color VARCHAR(50),
            theme VARCHAR(100),
            default_view VARCHAR(50) DEFAULT 'list',
            max_attachments INTEGER DEFAULT 5,
            allow_rename BOOLEAN DEFAULT TRUE,
            allow_copy BOOLEAN DEFAULT FALSE,
            track_changes BOOLEAN DEFAULT FALSE,
            track_seen BOOLEAN DEFAULT FALSE,
            queue_documents BOOLEAN DEFAULT FALSE,
            quick_entry BOOLEAN DEFAULT FALSE,
            sort_field VARCHAR(255),
            sort_order VARCHAR(10) DEFAULT 'ASC',
            search_fields TEXT,
            title_field VARCHAR(255),
            image_field VARCHAR(255),
            enable_auto_repeat BOOLEAN DEFAULT FALSE,
            document_type_class VARCHAR(255),
            enabled BOOLEAN DEFAULT TRUE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    ]

    portal_statements = [
        """
        CREATE TABLE IF NOT EXISTS "tabPortalUser" (
            name VARCHAR(255) PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            phone VARCHAR(50),
            display_name VARCHAR(255),
            username VARCHAR(255) UNIQUE,
            avatar VARCHAR(512),
            language VARCHAR(10) DEFAULT 'en',
            timezone VARCHAR(50) DEFAULT 'UTC',
            portal_role VARCHAR(255),
            linked_doctype VARCHAR(255),
            linked_docname VARCHAR(255),
            account_status VARCHAR(50) NOT NULL DEFAULT 'active',
            email_verified BOOLEAN DEFAULT FALSE,
            phone_verified BOOLEAN DEFAULT FALSE,
            password_hash VARCHAR(255) NOT NULL,
            last_login TIMESTAMP,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabPortalRole" (
            name VARCHAR(255) PRIMARY KEY,
            role_name VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            enabled BOOLEAN DEFAULT TRUE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabPortalPermission" (
            name VARCHAR(255) PRIMARY KEY,
            parent VARCHAR(255) NOT NULL,
            portal_role VARCHAR(255) NOT NULL,
            permlevel INTEGER DEFAULT 0,
            "read" BOOLEAN DEFAULT FALSE,
            "write" BOOLEAN DEFAULT FALSE,
            "create" BOOLEAN DEFAULT FALSE,
            "delete" BOOLEAN DEFAULT FALSE,
            "comment" BOOLEAN DEFAULT FALSE,
            "upload" BOOLEAN DEFAULT FALSE,
            "download" BOOLEAN DEFAULT FALSE,
            "export" BOOLEAN DEFAULT FALSE,
            "run_action" BOOLEAN DEFAULT FALSE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabPortalSession" (
            name VARCHAR(255) PRIMARY KEY,
            user_name VARCHAR(255) NOT NULL,
            token VARCHAR(255) NOT NULL UNIQUE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL
        );
        """,
    ]

    phase4_statements = [
        """
        CREATE TABLE IF NOT EXISTS "tabFieldPermission" (
            name VARCHAR(255) PRIMARY KEY,
            parent VARCHAR(255) NOT NULL,
            field_name VARCHAR(255) NOT NULL,
            role VARCHAR(255) NOT NULL,
            permlevel INTEGER DEFAULT 0,
            "read" BOOLEAN DEFAULT TRUE,
            "write" BOOLEAN DEFAULT TRUE,
            enabled BOOLEAN DEFAULT TRUE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabDataMaskRule" (
            name VARCHAR(255) PRIMARY KEY,
            parent VARCHAR(255) NOT NULL,
            field_name VARCHAR(255) NOT NULL,
            role VARCHAR(255),
            mask_type VARCHAR(50) NOT NULL DEFAULT 'partial',
            mask_character VARCHAR(10) DEFAULT '*',
            unmasked_prefix_len INTEGER DEFAULT 0,
            unmasked_suffix_len INTEGER DEFAULT 0,
            condition TEXT,
            enabled BOOLEAN DEFAULT TRUE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabPermissionRule" (
            name VARCHAR(255) PRIMARY KEY,
            parent VARCHAR(255) NOT NULL,
            role VARCHAR(255) NOT NULL,
            permlevel INTEGER DEFAULT 0,
            "read" BOOLEAN DEFAULT FALSE,
            "write" BOOLEAN DEFAULT FALSE,
            "create" BOOLEAN DEFAULT FALSE,
            "delete" BOOLEAN DEFAULT FALSE,
            "select" BOOLEAN DEFAULT FALSE,
            "amend" BOOLEAN DEFAULT FALSE,
            "condition" TEXT,
            apply_to_child BOOLEAN DEFAULT FALSE,
            enabled BOOLEAN DEFAULT TRUE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    ]

    phase3_statements = [
        """
        CREATE TABLE IF NOT EXISTS "tabFieldRule" (
            name VARCHAR(255) PRIMARY KEY,
            parent VARCHAR(255) NOT NULL,
            field_name VARCHAR(255) NOT NULL,
            rule_type VARCHAR(50) NOT NULL DEFAULT 'mandatory_if',
            "value" TEXT,
            condition TEXT,
            error_message TEXT,
            enabled BOOLEAN DEFAULT TRUE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabFieldDependency" (
            name VARCHAR(255) PRIMARY KEY,
            parent VARCHAR(255) NOT NULL,
            field_name VARCHAR(255) NOT NULL,
            depends_on_field VARCHAR(255) NOT NULL,
            depends_on_value TEXT,
            action VARCHAR(50) NOT NULL DEFAULT 'show',
            enabled BOOLEAN DEFAULT TRUE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "tabComputedField" (
            name VARCHAR(255) PRIMARY KEY,
            parent VARCHAR(255) NOT NULL,
            field_name VARCHAR(255) NOT NULL,
            formula TEXT NOT NULL,
            fieldtype VARCHAR(100) DEFAULT 'Data',
            options TEXT,
            script_type VARCHAR(20) DEFAULT 'Python',
            enabled BOOLEAN DEFAULT TRUE,
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    ]

    alter_statements = [
        _tenant_alter("tabUser"),
        _tenant_alter("tabHas Role"),
        _tenant_alter("tabSession"),
        _tenant_alter("tabServer Script"),
        _tenant_alter("tabReport"),
        _tenant_alter("tabError Log"),
        'ALTER TABLE "tabError Log" ALTER COLUMN method TYPE VARCHAR(255);',
    ]

    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
        for stmt in phase2_statements:
            conn.execute(text(stmt))
        for stmt in phase3_statements:
            conn.execute(text(stmt))
        for stmt in phase4_statements:
            conn.execute(text(stmt))
        for stmt in portal_statements:
            conn.execute(text(stmt))
        for stmt in alter_statements:
            conn.execute(text(stmt))


def drop_core_tables(engine: Engine) -> None:
    table_names = [
        "tabDocPerm",
        "tabDocField",
        "tabDocType",
        "tabHas Role",
        "tabUser",
        "tabRole",
        "tabInstalled Module",
        "tabModule Def",
        "tabInstalled App",
        "tabReport",
        "tabServer Script",
        "tabError Log",
        "tabSession",
        "tabTenant",
        "tabCustomField",
        "tabPropertySetter",
        "tabDocTypeSetting",
        "tabFieldRule",
        "tabFieldDependency",
        "tabComputedField",
        "tabFieldPermission",
        "tabDataMaskRule",
        "tabPermissionRule",
        "tabPortalSession",
        "tabPortalPermission",
        "tabPortalRole",
        "tabPortalUser",
    ]

    with engine.begin() as conn:
        for table in table_names:
            conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))

from sqlalchemy import text
from sqlalchemy.engine import Engine


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
            method VARCHAR(10),
            user_name VARCHAR(255),
            status VARCHAR(50),
            idx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    ]

    with engine.begin() as conn:
        for stmt in statements:
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
    ]

    with engine.begin() as conn:
        for table in table_names:
            conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))

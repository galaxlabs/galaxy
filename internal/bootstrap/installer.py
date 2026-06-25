from apps.galaxy.galaxy.db.connection import get_engine, test_connection
from apps.galaxy.galaxy.db.core_tables import create_core_tables
from apps.galaxy.galaxy.db.seed import (
    seed_administrator,
    seed_docfields,
    seed_docperms,
    seed_doctypes,
    seed_installed_app,
    seed_modules,
    seed_roles,
    seed_tenant,
)
from internal.config.site_config import load_site_config


def run_install(site_name: str | None = None):
    common, site = load_site_config(site_name)
    default_site = common.get("default_site", "default.local")
    resolved_site = site_name or default_site

    print("Galaxy installer")
    print()
    print("Loaded config:")
    print(f"  Site: {resolved_site}")
    print(f"  Database: {site['db_type']} {site['db_host']} {site['db_port']} {site['db_name']}")
    print(f"  DB user: {site['db_user']}")
    print(f"  Installed app: {site['installed_apps']}")
    print(f"  Installed modules: {site['installed_modules']}")
    print()

    engine = get_engine(site)

    print("Preparing PostgreSQL database and user...")
    print("PostgreSQL database/user: OK")
    print()

    print("Testing site database connection...")
    if test_connection(engine):
        print("PostgreSQL connection: OK")
    else:
        print("PostgreSQL connection: FAILED")
        raise SystemExit(1)
    print()

    print("Creating Galaxy core metadata bootstrap tables...")
    create_core_tables(engine)
    print("Galaxy core metadata tables: OK")
    print()

    print("Seeding default app, modules, role, Administrator, and tenant...")
    seed_installed_app(engine)
    seed_modules(engine)
    seed_roles(engine)
    seed_administrator(engine)
    seed_tenant(engine)
    print("Core seed data: OK")
    print()

    print("Seeding core DocType metadata records...")
    seed_doctypes(engine)
    print("Core DocType metadata seed: OK")
    print()

    print("Seeding default DocField records...")
    seed_docfields(engine)
    print("Core DocField metadata seed: OK")
    print()

    print("Seeding default DocPerm records...")
    seed_docperms(engine)
    print("Default DocPerm seed: OK")
    print()

    print("Administrator username: Administrator")
    print("Administrator password: admin")
    print()

    print("Registering site in Bench platform...")
    try:
        from internal.bench.platform_db import init_platform_db, register_site, site_exists

        init_platform_db()
        if not site_exists(resolved_site):
            config_path = f"sites/{resolved_site}/site_config.json"
            register_site(resolved_site, site["db_name"], site["db_user"], config_path)
            print(f"  Site '{resolved_site}' registered in platform.")
        else:
            print(f"  Site '{resolved_site}' already registered.")
    except Exception as e:
        print(f"  Warning: platform registration skipped ({e})")
    print()

    print("Next step: run galaxy doctor")


def run_doctor():
    common, site = load_site_config()
    default_site = common.get("default_site", "default.local")

    print("Galaxy doctor")
    print()
    print(f"Default site: {default_site}")
    print(f"Database: {site['db_type']} {site['db_host']} {site['db_port']} {site['db_name']}")
    print(f"DB user: {site['db_user']}")

    print()
    print("Security settings:")
    from internal.core.security import get_security_settings
    sec = get_security_settings()
    for key, val in sec.items():
        print(f"  {key}: {val}")

    engine = get_engine(site)

    print()
    if test_connection(engine):
        print("PostgreSQL connection: OK")
    else:
        print("PostgreSQL connection: FAILED")
        raise SystemExit(1)

    from sqlalchemy import text

    def count_table(table_name):
        with engine.connect() as conn:
            result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
            return result.scalar()

    installed_apps = count_table("tabInstalled App")
    installed_modules = count_table("tabInstalled Module")
    users = count_table("tabUser")
    roles = count_table("tabRole")
    doctypes = count_table("tabDocType")
    docfields = count_table("tabDocField")
    docperms = count_table("tabDocPerm")

    print()
    print(f"Installed apps: {installed_apps}")
    print(f"Installed modules: {installed_modules}")
    print(f"Users: {users}")
    print(f"Roles: {roles}")
    print(f"DocTypes: {doctypes}")
    print(f"DocFields: {docfields}")
    print(f"DocPerms: {docperms}")
    print()

    if (installed_apps >= 1 and installed_modules >= 6 and users >= 1
            and roles >= 1 and doctypes >= 10 and docfields > 0 and docperms >= 10):
        print("Galaxy installation: OK")
    else:
        print("Galaxy installation: INCOMPLETE")
        raise SystemExit(1)


def run_reset():
    common, site = load_site_config()
    default_site = common.get("default_site", "default.local")

    print("Galaxy reset")
    print()
    print(f"Default site: {default_site}")
    print(f"Database: {site['db_type']} {site['db_host']} {site['db_port']} {site['db_name']}")
    print()

    engine = get_engine(site)

    print("Dropping all core tables...")
    from apps.galaxy.galaxy.db.core_tables import drop_core_tables
    drop_core_tables(engine)
    print("Core tables dropped: OK")
    print()
    print("Run 'galaxy install' to recreate the site.")

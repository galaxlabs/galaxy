from galaxy.database.seed import PHASE4_DOCFIELDS, PHASE4_DOCTYPES


def test_phase4_doctypes_count():
    assert len(PHASE4_DOCTYPES) == 3


def test_phase4_doctypes_include():
    assert "FieldPermission" in PHASE4_DOCTYPES
    assert "DataMaskRule" in PHASE4_DOCTYPES
    assert "PermissionRule" in PHASE4_DOCTYPES


def test_phase4_docfields_all_doctypes():
    for name in PHASE4_DOCTYPES:
        assert name in PHASE4_DOCFIELDS, f"Missing DocFields for {name}"


def test_phase4_docfields_have_fieldname():
    for parent, fields in PHASE4_DOCFIELDS.items():
        for field in fields:
            assert field[0], f"Empty fieldname in {parent}"


def test_phase4_docfields_have_fieldtype():
    for parent, fields in PHASE4_DOCFIELDS.items():
        for field in fields:
            assert field[2], f"Empty fieldtype in {parent} ({field[0]})"


def test_phase4_each_has_name_field():
    for dt_name, fields in PHASE4_DOCFIELDS.items():
        fieldnames = [f[0] for f in fields]
        assert "name" in fieldnames, f"{dt_name} missing 'name' field"


def test_phase4_each_has_parent_field():
    for dt_name, fields in PHASE4_DOCFIELDS.items():
        fieldnames = [f[0] for f in fields]
        assert "parent" in fieldnames, f"{dt_name} missing 'parent' field"


def test_phase4_each_has_role_field():
    for dt_name, fields in PHASE4_DOCFIELDS.items():
        fieldnames = [f[0] for f in fields]
        assert "role" in fieldnames, f"{dt_name} missing 'role' field"


def test_phase4_each_has_enabled_field():
    for dt_name, fields in PHASE4_DOCFIELDS.items():
        fieldnames = [f[0] for f in fields]
        assert "enabled" in fieldnames, f"{dt_name} missing 'enabled' field"

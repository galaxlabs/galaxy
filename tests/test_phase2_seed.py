from galaxy.database.seed import PHASE2_DOCFIELDS, PHASE2_DOCTYPES


def test_phase2_doctypes_count():
    assert len(PHASE2_DOCTYPES) == 3


def test_phase2_doctypes_include():
    assert "CustomField" in PHASE2_DOCTYPES
    assert "PropertySetter" in PHASE2_DOCTYPES
    assert "DocTypeSetting" in PHASE2_DOCTYPES


def test_phase2_docfields_all_doctypes():
    for name in PHASE2_DOCTYPES:
        assert name in PHASE2_DOCFIELDS, f"Missing DocFields for {name}"


def test_phase2_docfields_have_fieldname():
    for parent, fields in PHASE2_DOCFIELDS.items():
        for field in fields:
            fieldname = field[0]
            assert fieldname, f"Empty fieldname in {parent}"


def test_phase2_docfields_have_fieldtype():
    for parent, fields in PHASE2_DOCFIELDS.items():
        for field in fields:
            fieldtype = field[2]
            assert fieldtype, f"Empty fieldtype in {parent} ({field[0]})"


def test_phase2_each_has_name_field():
    for dt_name, fields in PHASE2_DOCFIELDS.items():
        fieldnames = [f[0] for f in fields]
        assert "name" in fieldnames, f"{dt_name} missing 'name' field"


def test_phase2_each_has_parent_field():
    for dt_name, fields in PHASE2_DOCFIELDS.items():
        fieldnames = [f[0] for f in fields]
        assert "parent" in fieldnames, f"{dt_name} missing 'parent' field"


def test_phase2_each_has_enabled_field():
    for dt_name, fields in PHASE2_DOCFIELDS.items():
        fieldnames = [f[0] for f in fields]
        assert "enabled" in fieldnames, f"{dt_name} missing 'enabled' field"

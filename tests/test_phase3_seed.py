from galaxy.database.seed import PHASE3_DOCFIELDS, PHASE3_DOCTYPES


def test_phase3_doctypes_count():
    assert len(PHASE3_DOCTYPES) == 3


def test_phase3_doctypes_include():
    assert "FieldRule" in PHASE3_DOCTYPES
    assert "FieldDependency" in PHASE3_DOCTYPES
    assert "ComputedField" in PHASE3_DOCTYPES


def test_phase3_docfields_all_doctypes():
    for name in PHASE3_DOCTYPES:
        assert name in PHASE3_DOCFIELDS, f"Missing DocFields for {name}"


def test_phase3_docfields_have_fieldname():
    for parent, fields in PHASE3_DOCFIELDS.items():
        for field in fields:
            assert field[0], f"Empty fieldname in {parent}"


def test_phase3_docfields_have_fieldtype():
    for parent, fields in PHASE3_DOCFIELDS.items():
        for field in fields:
            assert field[2], f"Empty fieldtype in {parent} ({field[0]})"


def test_phase3_each_has_name_field():
    for dt_name, fields in PHASE3_DOCFIELDS.items():
        fieldnames = [f[0] for f in fields]
        assert "name" in fieldnames, f"{dt_name} missing 'name' field"


def test_phase3_each_has_parent_field():
    for dt_name, fields in PHASE3_DOCFIELDS.items():
        fieldnames = [f[0] for f in fields]
        assert "parent" in fieldnames, f"{dt_name} missing 'parent' field"


def test_phase3_each_has_field_name():
    for dt_name, fields in PHASE3_DOCFIELDS.items():
        fieldnames = [f[0] for f in fields]
        assert "field_name" in fieldnames, f"{dt_name} missing 'field_name' field"


def test_phase3_each_has_enabled_field():
    for dt_name, fields in PHASE3_DOCFIELDS.items():
        fieldnames = [f[0] for f in fields]
        assert "enabled" in fieldnames, f"{dt_name} missing 'enabled' field"

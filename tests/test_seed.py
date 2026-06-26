from galaxy.database.seed import DOCFIELDS, DOCTYPES


def test_doctypes_count():
    assert len(DOCTYPES) == 13


def test_doctypes_include_core():
    names = [dt[0] for dt in DOCTYPES]
    assert "DocType" in names
    assert "DocField" in names
    assert "DocPerm" in names
    assert "User" in names
    assert "Role" in names
    assert "Has Role" in names
    assert "Error Log" in names
    assert "Installed App" in names
    assert "Installed Module" in names
    assert "Module Def" in names
    assert "Server Script" in names
    assert "Report" in names
    assert "Session" in names


def test_docfields_all_doctypes():
    doctype_names = [dt[0] for dt in DOCTYPES]
    for name in doctype_names:
        assert name in DOCFIELDS, f"Missing DocFields for {name}"


def test_docfields_have_fieldname():
    for parent, fields in DOCFIELDS.items():
        for field in fields:
            fieldname = field[0]
            assert fieldname, f"Empty fieldname in {parent}"


def test_docfields_have_fieldtype():
    for parent, fields in DOCFIELDS.items():
        for field in fields:
            fieldtype = field[2]
            assert fieldtype, f"Empty fieldtype in {parent} ({field[0]})"


def test_each_doctype_has_name_field():
    for dt_name, fields in DOCFIELDS.items():
        fieldnames = [f[0] for f in fields]
        assert "name" in fieldnames, f"{dt_name} missing 'name' field"

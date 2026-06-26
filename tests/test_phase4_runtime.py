import pytest
from sqlalchemy import text

from galaxy.config import load_site_config
from galaxy.database.connection import get_engine
from galaxy.model.runtimemeta import merge_meta, RuntimeMeta
from galaxy.model.permission_engine import (
    apply_field_permissions,
    apply_data_masks,
    check_permission_rule,
    filter_list_by_permission,
    get_field_restrictions,
    get_effective_mask_rules,
)


def _make_meta(**kwargs) -> RuntimeMeta:
    base = {
        "doctype": {"name": "TestDoc", "module": "Core", "app_name": "core", "table_name": "tabTestDoc"},
        "fields": [],
        "permissions": [],
        "custom_fields": [],
        "property_setters": [],
        "settings": [],
        "field_rules": [],
        "field_dependencies": [],
        "computed_fields": [],
        "field_permissions": [],
        "field_perms_map": {},
        "data_mask_rules": [],
        "data_mask_map": {},
        "permission_rules": [],
        "display_logic": [],
        "display_logic_map": {},
        "dynamic_sources": {},
    }
    base.update(kwargs)
    return RuntimeMeta(**base)


class TestFieldPermissions:
    def test_no_restrictions_passes_through(self):
        doc = {"name": "doc1", "doctype": "Test", "secret": "xyz"}
        result = apply_field_permissions(doc, "User", [])
        assert result == doc

    def test_read_fields_filter(self):
        doc = {"name": "doc1", "doctype": "Test", "secret": "xyz", "public": "abc"}
        result = apply_field_permissions(doc, "User", ["name", "public"])
        assert "name" in result
        assert "public" in result
        assert "secret" not in result

    def test_doctype_and_name_always_present(self):
        doc = {"name": "doc1", "doctype": "Test", "a": "1", "b": "2"}
        result = apply_field_permissions(doc, "User", ["a"])
        assert "name" in result
        assert "doctype" in result
        assert "a" in result
        assert "b" not in result

    def test_field_restrictions_from_meta(self):
        meta = _make_meta(
            field_permissions=[
                {"field_name": "secret", "role": "User", "read": False, "write": False, "enabled": True},
                {"field_name": "name", "role": "User", "read": True, "write": False, "enabled": True},
            ]
        )
        read_fields, write_fields = get_field_restrictions(meta, "User")
        assert read_fields == ["name"]
        assert write_fields == []

    def test_no_role_permissions_returns_none(self):
        meta = _make_meta(
            field_permissions=[
                {"field_name": "secret", "role": "Admin", "read": True, "write": True, "enabled": True},
            ]
        )
        read_fields, write_fields = get_field_restrictions(meta, "User")
        assert read_fields is None

    def test_disabled_permissions_ignored(self):
        meta = _make_meta(
            field_permissions=[
                {"field_name": "secret", "role": "User", "read": True, "write": True, "enabled": False},
            ]
        )
        read_fields, write_fields = get_field_restrictions(meta, "User")
        assert read_fields is None


class TestDataMask:
    def test_no_masks_passes_through(self):
        doc = {"name": "doc1", "email": "test@example.com"}
        result = apply_data_masks(doc, "User", [])
        assert result == doc

    def test_full_mask(self):
        doc = {"name": "doc1", "secret": "hello"}
        rules = [{"field_name": "secret", "mask_type": "full", "mask_character": "*", "unmasked_prefix_len": 0, "unmasked_suffix_len": 0}]
        result = apply_data_masks(doc, "User", rules)
        assert result["secret"] == "*****"

    def test_partial_mask(self):
        doc = {"name": "doc1", "card": "1234567890"}
        rules = [{"field_name": "card", "mask_type": "partial", "mask_character": "*", "unmasked_prefix_len": 4, "unmasked_suffix_len": 2}]
        result = apply_data_masks(doc, "User", rules)
        assert result["card"] == "1234****90"

    def test_email_mask(self):
        doc = {"name": "doc1", "email": "user@example.com"}
        rules = [{"field_name": "email", "mask_type": "email", "mask_character": "*", "unmasked_prefix_len": 0, "unmasked_suffix_len": 0}]
        result = apply_data_masks(doc, "User", rules)
        assert result["email"] == "u***@example.com"

    def test_phone_mask(self):
        doc = {"name": "doc1", "phone": "1234567890"}
        rules = [{"field_name": "phone", "mask_type": "phone", "mask_character": "*", "unmasked_prefix_len": 0, "unmasked_suffix_len": 0}]
        result = apply_data_masks(doc, "User", rules)
        assert result["phone"] == "******7890"

    def test_mask_none_value(self):
        doc = {"name": "doc1", "secret": None}
        rules = [{"field_name": "secret", "mask_type": "full", "mask_character": "*", "unmasked_prefix_len": 0, "unmasked_suffix_len": 0}]
        result = apply_data_masks(doc, "User", rules)
        assert result["secret"] is None

    def test_condition_evaluates_true(self):
        doc = {"name": "doc1", "secret": "visible", "role": "admin"}
        rules = [{
            "field_name": "secret", "mask_type": "full", "mask_character": "*",
            "unmasked_prefix_len": 0, "unmasked_suffix_len": 0,
            "condition": "role == 'admin'",
        }]
        result = apply_data_masks(doc, "User", rules)
        assert result["secret"] == "*******"

    def test_condition_evaluates_false(self):
        doc = {"name": "doc1", "secret": "visible", "role": "user"}
        rules = [{
            "field_name": "secret", "mask_type": "full", "mask_character": "*",
            "unmasked_prefix_len": 0, "unmasked_suffix_len": 0,
            "condition": "role == 'admin'",
        }]
        result = apply_data_masks(doc, "User", rules)
        assert result["secret"] == "visible"

    def test_get_effective_masks(self):
        meta = _make_meta(
            data_mask_rules=[
                {"field_name": "s1", "mask_type": "full", "role": "User", "enabled": True},
                {"field_name": "s2", "mask_type": "full", "role": "Admin", "enabled": True},
                {"field_name": "s3", "mask_type": "full", "role": "User", "enabled": False},
            ]
        )
        masks = get_effective_mask_rules(meta, "User")
        assert len(masks) == 1
        assert masks[0]["field_name"] == "s1"


class TestPermissionRules:
    def test_no_rules_allowed(self):
        assert check_permission_rule([], "User", {"name": "x"}, "read") is True

    def test_matching_role_with_condition_allowed(self):
        rules = [{
            "role": "User", "read": True, "enabled": True,
            "condition": "doc_type == 'special'",
        }]
        assert check_permission_rule(rules, "User", {"name": "x", "doc_type": "special"}, "read") is True

    def test_matching_role_with_condition_denied(self):
        rules = [{
            "role": "User", "read": True, "enabled": True,
            "condition": "doc_type == 'special'",
        }]
        assert check_permission_rule(rules, "User", {"name": "x", "doc_type": "normal"}, "read") is False

    def test_disabled_rule_skipped(self):
        rules = [
            {"role": "User", "read": True, "enabled": False},
        ]
        assert check_permission_rule(rules, "User", {"name": "x"}, "read") is True

    def test_no_read_grant_for_role(self):
        rules = [
            {"role": "Admin", "read": True, "enabled": True},
            {"role": "User", "write": True, "enabled": True},
        ]
        assert check_permission_rule(rules, "User", {"name": "x"}, "read") is True

    def test_filter_list(self):
        docs = [
            {"name": "d1", "owner": "alice"},
            {"name": "d2", "owner": "bob"},
            {"name": "d3", "owner": "alice"},
        ]
        rules = [{
            "role": "User", "read": True, "enabled": True,
            "condition": "owner == 'alice'",
        }]
        result = filter_list_by_permission(docs, "User", rules, "read")
        assert len(result) == 2
        assert all(d["owner"] == "alice" for d in result)

    def test_filter_list_no_rules(self):
        docs = [{"name": "d1"}, {"name": "d2"}]
        result = filter_list_by_permission(docs, "User", [], "read")
        assert len(result) == 2


class TestPhase4Integration:
    def test_full_field_permission_pipeline(self):
        meta = _make_meta(
            field_permissions=[
                {"field_name": "email", "role": "Viewer", "read": True, "write": False, "enabled": True},
                {"field_name": "salary", "role": "Viewer", "read": False, "write": False, "enabled": True},
            ],
            data_mask_rules=[
                {"field_name": "email", "mask_type": "email", "role": "Viewer", "enabled": True},
            ],
        )

        doc = {"name": "e1", "doctype": "Employee", "email": "john@corp.com", "salary": 100000, "department": "Eng"}

        read_fields, _ = get_field_restrictions(meta, "Viewer")
        assert read_fields == ["email"]

        result = apply_field_permissions(doc, "Viewer", read_fields)
        assert "email" in result
        assert "name" in result
        assert "doctype" in result
        assert "salary" not in result
        assert "department" not in result

        masks = get_effective_mask_rules(meta, "Viewer")
        result = apply_data_masks(result, "Viewer", masks)
        assert result["email"] == "j***@corp.com"

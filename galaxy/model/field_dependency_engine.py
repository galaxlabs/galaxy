from typing import Any

from galaxy.model.field_rule_engine import _safe_eval
from galaxy.model.runtimemeta import RuntimeMeta


def _compare_values(actual: Any, operator: str, expected: Any) -> bool:
    if isinstance(actual, str) and isinstance(expected, (int, float)):
        try:
            actual = type(expected)(actual)
        except (ValueError, TypeError):
            pass
    elif isinstance(expected, str) and isinstance(actual, (int, float)):
        try:
            expected = type(actual)(expected)
        except (ValueError, TypeError):
            pass
    if operator == "=":
        return actual == expected
    if operator == "!=":
        return actual != expected
    if operator == "in":
        if isinstance(expected, str):
            return actual in [v.strip() for v in expected.split("\n") if v.strip()]
        if isinstance(expected, (list, tuple)):
            return actual in expected
        return False
    if operator == "not in":
        if isinstance(expected, str):
            return actual not in [v.strip() for v in expected.split("\n") if v.strip()]
        if isinstance(expected, (list, tuple)):
            return actual not in expected
        return True
    if operator == ">":
        try:
            return float(actual) > float(expected)
        except (ValueError, TypeError):
            return False
    if operator == "<":
        try:
            return float(actual) < float(expected)
        except (ValueError, TypeError):
            return False
    if operator == ">=":
        try:
            return float(actual) >= float(expected)
        except (ValueError, TypeError):
            return False
    if operator == "<=":
        try:
            return float(actual) <= float(expected)
        except (ValueError, TypeError):
            return False
    if operator == "is_set":
        return actual is not None and actual != ""
    if operator == "is_not_set":
        return actual is None or actual == ""
    return False


def evaluate_dependency(dep: dict, doc_data: dict) -> bool:
    if not dep.get("enabled", True):
        return False

    condition = dep.get("condition", "")
    if condition:
        ctx = {**doc_data, "doc": doc_data}
        result = _safe_eval(condition, ctx)
        return bool(result) if result is not None else False

    depends_on = dep.get("depends_on_field", "")
    if not depends_on:
        return True

    actual = doc_data.get(depends_on)
    expected = dep.get("depends_on_value", "")
    operator = dep.get("operator", "=")
    return _compare_values(actual, operator, expected)


def resolve_field_dependencies(meta: RuntimeMeta, doc_data: dict) -> dict[str, list[dict[str, Any]]]:
    results: dict[str, list[dict[str, Any]]] = {}

    for dep in meta.field_dependencies:
        if not dep.get("enabled", True):
            continue

        field_name = dep.get("field_name", "")
        if not field_name:
            continue

        effective = evaluate_dependency(dep, doc_data)
        field = meta.get_field(field_name)
        label = field.get("label") or field_name if field else field_name

        action = dep.get("action", "show")
        if action not in ("show", "hide", "require", "readonly", "filter_options", "set_default"):
            action = "show"

        entry = {
            "action": action,
            "effective": effective,
            "depends_on_field": dep.get("depends_on_field", ""),
            "depends_on_value": dep.get("depends_on_value", ""),
            "label": label,
        }

        if dep.get("action") == "set_default":
            entry["default_value"] = dep.get("value", "")

        results.setdefault(field_name, []).append(entry)

    return results


def get_effective_field_states(meta: RuntimeMeta, doc_data: dict) -> dict[str, dict[str, Any]]:
    deps = resolve_field_dependencies(meta, doc_data)
    states: dict[str, dict[str, Any]] = {}

    for field in meta.fields:
        fname = field["fieldname"]
        states[fname] = {
            "hidden": field.get("hidden", False),
            "required": field.get("reqd", False),
            "read_only": field.get("read_only", False),
        }

    for fname, entries in deps.items():
        for entry in entries:
            if entry["action"] == "hide":
                states.setdefault(fname, {})["hidden"] = entry["effective"]
            elif entry["action"] == "show":
                states.setdefault(fname, {})["hidden"] = not entry["effective"]
            elif entry["action"] == "require":
                states.setdefault(fname, {})["required"] = entry["effective"]
            elif entry["action"] == "readonly":
                states.setdefault(fname, {})["read_only"] = entry["effective"]

    return states

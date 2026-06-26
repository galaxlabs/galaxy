from galaxy.model.field_dependency_engine import _compare_values
from galaxy.model.runtimemeta import RuntimeMeta


def resolve_display_logic(meta: RuntimeMeta, doc_data: dict) -> dict[str, list[dict]]:
    results: dict[str, list[dict]] = {}

    for rule in meta.display_logic:
        if not rule.get("enabled", True):
            continue

        field_name = rule.get("field_name", "")
        if not field_name:
            continue

        depends_on = rule.get("depends_on_field", "")
        if not depends_on:
            continue

        actual = doc_data.get(depends_on)
        expected = rule.get("value", "")
        operator = rule.get("operator", "=")
        effective = _compare_values(actual, operator, expected)

        action = rule.get("action", "show")

        entry = {
            "action": action,
            "effective": effective,
            "depends_on_field": depends_on,
            "value": expected,
            "condition_group": rule.get("condition_group", ""),
            "priority": rule.get("priority", 0),
        }

        results.setdefault(field_name, []).append(entry)

    return results


def get_effective_visibility(meta: RuntimeMeta, doc_data: dict) -> dict[str, dict]:
    resolved = resolve_display_logic(meta, doc_data)
    states: dict[str, dict] = {}

    for field in meta.fields:
        fname = field["fieldname"]
        states[fname] = {
            "hidden": field.get("hidden", False),
            "required": field.get("reqd", False),
            "read_only": field.get("read_only", False),
        }

    for fname, entries in resolved.items():
        for entry in entries:
            if not entry["effective"]:
                continue
            if entry["action"] == "hide":
                states.setdefault(fname, {})["hidden"] = True
            elif entry["action"] == "show":
                states.setdefault(fname, {})["hidden"] = False
            elif entry["action"] == "require":
                states.setdefault(fname, {})["required"] = True
            elif entry["action"] == "readonly":
                states.setdefault(fname, {})["read_only"] = True

    return states

from typing import Any

from galaxy.core.doctype.field_rule_engine import _safe_eval
from galaxy.core.doctype.runtimemeta import RuntimeMeta


def evaluate_computed_field(
    computed_field: dict[str, Any],
    doc_data: dict[str, Any],
) -> Any:
    formula = computed_field.get("formula", "")
    if not formula:
        return None

    ctx = {**doc_data, "doc": doc_data}
    result = _safe_eval(formula, ctx)
    return result


def evaluate_computed_fields(
    meta: RuntimeMeta,
    doc_data: dict[str, Any],
) -> dict[str, Any]:
    results: dict[str, Any] = {}

    for cf in meta.computed_fields:
        if not cf.get("enabled", True):
            continue

        field_name = cf.get("field_name", "")
        if not field_name:
            continue

        value = evaluate_computed_field(cf, doc_data)
        if value is not None:
            results[field_name] = value

    return results


def evaluate_and_apply_computed_fields(
    meta: RuntimeMeta,
    doc_data: dict[str, Any],
) -> dict[str, Any]:
    computed = evaluate_computed_fields(meta, doc_data)
    result = dict(doc_data)
    for key, val in computed.items():
        result[key] = val
    return result

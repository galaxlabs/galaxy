import ast
import operator as py_operator
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from galaxy.core.doctype.runtimemeta import RuntimeMeta

_UNARY_OPS = {ast.UAdd: py_operator.pos, ast.USub: py_operator.neg, ast.Not: py_operator.not_}
_BIN_OPS = {
    ast.Add: py_operator.add, ast.Sub: py_operator.sub, ast.Mult: py_operator.mul,
    ast.Div: py_operator.truediv, ast.FloorDiv: py_operator.floordiv, ast.Mod: py_operator.mod,
    ast.Pow: py_operator.pow,
}
_CMP_OPS = {
    ast.Eq: py_operator.eq, ast.NotEq: py_operator.ne, ast.Lt: py_operator.lt,
    ast.LtE: py_operator.le, ast.Gt: py_operator.gt, ast.GtE: py_operator.ge,
    ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b,
}
_ALLOWED_NAMES = {
    "str": str, "int": int, "float": float, "bool": bool, "len": len,
    "abs": abs, "round": round, "min": min, "max": max, "sum": sum,
    "date": date, "datetime": datetime, "Decimal": Decimal,
    "True": True, "False": False, "None": None,
}


def _safe_eval(expression: str, context: dict[str, Any]) -> Any:
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        return None

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in context:
                return context[node.id]
            if node.id in _ALLOWED_NAMES:
                return _ALLOWED_NAMES[node.id]
            raise NameError(f"Name '{node.id}' is not allowed")
        if isinstance(node, ast.UnaryOp):
            return _UNARY_OPS[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.BinOp):
            return _BIN_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.Compare):
            left = _eval(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                right = _eval(comparator)
                if not _CMP_OPS[type(op)](left, right):
                    return False
            return True
        if isinstance(node, ast.BoolOp):
            results = [_eval(v) for v in node.values]
            if isinstance(node.op, ast.And):
                return all(results)
            return any(results)
        if isinstance(node, ast.Call):
            func = _eval(node.func)
            args = [_eval(a) for a in node.args]
            return func(*args)
        if isinstance(node, ast.Attribute):
            value = _eval(node.value)
            if hasattr(value, node.attr):
                return getattr(value, node.attr)
            if isinstance(value, dict):
                return value.get(node.attr)
        if isinstance(node, ast.Subscript):
            value = _eval(node.value)
            slice_val = _eval(node.slice)
            if isinstance(value, (dict, list)):
                return value[slice_val]
            if isinstance(value, str) and isinstance(slice_val, (int, slice)):
                return value[slice_val]
        if isinstance(node, ast.List):
            return [_eval(el) for el in node.elts]
        if isinstance(node, ast.Dict):
            return {_eval(k): _eval(v) for k, v in zip(node.keys, node.nodes)}
        if isinstance(node, ast.Tuple):
            return tuple(_eval(el) for el in node.elts)
        if isinstance(node, ast.Slice):
            return slice(
                _eval(node.lower) if node.lower else None,
                _eval(node.upper) if node.upper else None,
                _eval(node.step) if node.step else None,
            )
        raise ValueError(f"Unsupported expression: {type(node).__name__}")

    try:
        return _eval(tree)
    except Exception:
        return None


def _get_doc_value(doc_data: dict, field_name: str) -> Any:
    return doc_data.get(field_name)


def _evaluate_rule_condition(rule: dict, doc_data: dict) -> bool:
    condition = rule.get("condition", "")
    if not condition:
        return True

    ctx = {**doc_data, "doc": doc_data}
    result = _safe_eval(condition, ctx)
    return bool(result) if result is not None else False


def validate_field_rules(meta: RuntimeMeta, doc_data: dict) -> list[str]:
    errors: list[str] = []

    for rule in meta.field_rules:
        if not rule.get("enabled", True):
            continue
        if not _evaluate_rule_condition(rule, doc_data):
            continue

        field_name = rule["field_name"]
        value = _get_doc_value(doc_data, field_name)
        label = field_name
        field = meta.get_field(field_name)
        if field:
            label = field.get("label") or field_name

        rule_type = rule.get("rule_type", "")
        rule_value = rule.get("value")

        if rule_type == "required" and not value and value != 0:
            errors.append(f"{label} is required.")
        elif rule_type == "min_value" and value is not None:
            try:
                if float(value) < float(rule_value):
                    errors.append(f"{label} must be at least {rule_value}.")
            except (ValueError, TypeError):
                pass
        elif rule_type == "max_value" and value is not None:
            try:
                if float(value) > float(rule_value):
                    errors.append(f"{label} must be at most {rule_value}.")
            except (ValueError, TypeError):
                pass
        elif rule_type == "min_length" and isinstance(value, str):
            try:
                if len(value) < int(rule_value):
                    errors.append(f"{label} must be at least {rule_value} characters.")
            except (ValueError, TypeError):
                pass
        elif rule_type == "max_length" and isinstance(value, str):
            try:
                if len(value) > int(rule_value):
                    errors.append(f"{label} must be at most {rule_value} characters.")
            except (ValueError, TypeError):
                pass
        elif rule_type == "regex" and isinstance(value, str):
            import re
            try:
                if not re.match(rule_value, value):
                    errors.append(f"{label} has an invalid format.")
            except re.error:
                pass
        elif rule_type == "unique" and value is not None:
            from galaxy.core.repository import _count_field_value
            doctype_name = meta.doctype.get("name", "")
            name = doc_data.get("name")
            try:
                count = _count_field_value(doctype_name, field_name, value, exclude_name=name)
                if count and count > 0:
                    errors.append(f"{label} '{value}' already exists.")
            except Exception:
                pass
        elif rule_type == "mandatory_if" and not value:
            errors.append(f"{label} is required in this context.")

    return errors


def apply_field_rules_to_meta(meta: RuntimeMeta) -> RuntimeMeta:
    return meta

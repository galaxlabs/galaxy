import json
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Callable


Coercer = Callable[[Any], Any]
Validator = Callable[[Any, dict], str | None]


@dataclass
class FieldTypeDef:
    name: str
    python_type: type = str
    sql_type: str = "TEXT"
    coercer: Coercer | None = None
    validator: Validator | None = None
    default_value: Any = None
    options_required: bool = False
    skip_in_crud: bool = False
    sortable: bool = True


_field_types: dict[str, FieldTypeDef] = {}


def _int_coerce(v):
    if v is None:
        return 0
    try:
        return int(v)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid integer: {v!r}")


def _float_coerce(v):
    if v is None:
        return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid number: {v!r}")


def _check_coerce(v):
    return 1 if v else 0


def _json_coerce(v):
    if not isinstance(v, str):
        return json.dumps(v, ensure_ascii=False, default=str)
    return v


def _datetime_coerce(v):
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, str):
        return v
    return str(v) if v is not None else None


def _date_coerce(v):
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, str):
        return v
    return str(v) if v is not None else None


_BUILTIN_TYPES: list[FieldTypeDef] = [
    FieldTypeDef("Data", str, "TEXT", sortable=True),
    FieldTypeDef("Small Text", str, "TEXT", sortable=False),
    FieldTypeDef("Long Text", str, "TEXT", sortable=False),
    FieldTypeDef("Int", int, "INTEGER", coercer=_int_coerce, default_value=0, sortable=True),
    FieldTypeDef("Float", float, "DOUBLE PRECISION", coercer=_float_coerce, default_value=0.0, sortable=True),
    FieldTypeDef("Currency", float, "DOUBLE PRECISION", coercer=_float_coerce, default_value=0.0, sortable=True),
    FieldTypeDef("Check", int, "SMALLINT", coercer=_check_coerce, default_value=0, sortable=True),
    FieldTypeDef("Date", str, "DATE", coercer=_date_coerce, sortable=True),
    FieldTypeDef("Datetime", str, "TIMESTAMP", coercer=_datetime_coerce, sortable=True),
    FieldTypeDef("Select", str, "TEXT", options_required=True, sortable=True),
    FieldTypeDef("Link", str, "TEXT", options_required=True, sortable=True),
    FieldTypeDef("Table", list, "TEXT", options_required=True, skip_in_crud=True, sortable=False),
    FieldTypeDef("Attach", str, "TEXT", sortable=False),
    FieldTypeDef("JSON", (dict, list, str), "JSONB", coercer=_json_coerce, sortable=False),
    FieldTypeDef("Code", str, "TEXT", sortable=False),
]


def register_type(td: FieldTypeDef) -> None:
    _field_types[td.name] = td


def get_type(name: str) -> FieldTypeDef | None:
    return _field_types.get(name)


def get_all_types() -> dict[str, FieldTypeDef]:
    return dict(_field_types)


def coerce(fieldtype: str, value: Any) -> Any:
    td = get_type(fieldtype)
    if td and td.coercer:
        return td.coercer(value)
    if value is None:
        return None
    return value


def validate(fieldtype: str, value: Any, field: dict) -> str | None:
    td = get_type(fieldtype)
    if td and td.validator:
        return td.validator(value, field)
    return None


def sql_type(fieldtype: str) -> str:
    td = get_type(fieldtype)
    return td.sql_type if td else "TEXT"


def is_valid(fieldtype: str) -> bool:
    return fieldtype in _field_types


def options_required(fieldtype: str) -> bool:
    td = get_type(fieldtype)
    return td.options_required if td else False


def skip_in_crud(fieldtype: str) -> bool:
    td = get_type(fieldtype)
    return td.skip_in_crud if td else False


def is_sortable(fieldtype: str) -> bool:
    td = get_type(fieldtype)
    return td.sortable if td else False


for _td in _BUILTIN_TYPES:
    register_type(_td)


__all__ = [
    "register_type", "get_type", "get_all_types",
    "coerce", "validate", "sql_type", "is_valid",
    "options_required", "skip_in_crud", "is_sortable",
    "FieldTypeDef",
]

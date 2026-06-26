import csv
import io
import json

from galaxy.model.document import create_document, get_crud_fields
from galaxy.model.field_type_registry import is_valid as valid_fieldtype


def _detect_delimiter(sample: str) -> str:
    if "\t" in sample:
        return "\t"
    return ","


def _parse_csv(content: str, delimiter: str | None = None) -> tuple[list[str], list[list[str]]]:
    if delimiter is None:
        delimiter = _detect_delimiter(content[:2000])
    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
    rows = list(reader)
    if not rows:
        return [], []
    headers = [h.strip() for h in rows[0]]
    data = rows[1:]
    return headers, data


def _parse_json(content: str) -> list[dict]:
    data = json.loads(content)
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("JSON must be an object or array of objects.")
    return data


def _parse_excel(content: bytes) -> tuple[list[str], list[list[str]]]:
    try:
        import openpyxl
    except ImportError:
        raise RuntimeError("openpyxl is required for Excel import. Install with: pip install openpyxl")
    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return [], []
    headers = [str(h).strip() if h is not None else "" for h in rows[0]]
    data = []
    for row in rows[1:]:
        data.append([str(c) if c is not None else "" for c in row])
    wb.close()
    return headers, data


def _build_field_map(headers: list[str], doctype_fields: list[dict], field_mapping: dict[str, str] | None = None) -> dict[str, str]:
    field_map: dict[str, str] = {}
    valid_names = {f["fieldname"] for f in doctype_fields} | {"name"}
    for i, header in enumerate(headers):
        target = (field_mapping or {}).get(header, header)
        if target in valid_names:
            field_map[header] = target
        else:
            field_map[header] = header
    return field_map


def _row_to_dict(headers: list[str], row: list, field_map: dict[str, str]) -> dict:
    result: dict = {}
    for i, val in enumerate(row):
        if i >= len(headers):
            break
        mapped = field_map.get(headers[i])
        if not mapped:
            continue
        if isinstance(val, str):
            val = val.strip()
        if val or val == 0 or val is False:
            result[mapped] = val
    return result


def import_csv(doctype: str, content: str, field_mapping: dict[str, str] | None = None, delimiter: str | None = None) -> dict:
    headers, rows = _parse_csv(content, delimiter)
    return _import_rows(doctype, headers, rows, field_mapping)


def import_json(doctype: str, content: str) -> dict:
    records = _parse_json(content)
    headers = list(set().union(*(r.keys() for r in records))) if records else []
    rows = [[r.get(h, "") for h in headers] for r in records]
    return _import_rows(doctype, headers, rows, None)


def import_excel(doctype: str, content: bytes, field_mapping: dict[str, str] | None = None) -> dict:
    headers, rows = _parse_excel(content)
    return _import_rows(doctype, headers, rows, field_mapping)


def _import_rows(doctype: str, headers: list[str], rows: list[list[str]], field_mapping: dict[str, str] | None = None) -> dict:
    fields = get_crud_fields(doctype)
    field_map = _build_field_map(headers, fields, field_mapping)
    success_count = 0
    error_count = 0
    errors: list[dict] = []
    created: list[str] = []

    for row_idx, row in enumerate(rows):
        doc_data = _row_to_dict(headers, row, field_map)
        if not doc_data:
            continue
        result = create_document(doctype, doc_data)
        if result.get("success"):
            success_count += 1
            doc_name = result.get("data", {}).get("name", "")
            created.append(doc_name)
        else:
            error_count += 1
            errors.append({
                "row": row_idx + 2,
                "data": doc_data,
                "error": result.get("error", "Unknown error"),
                "details": result.get("errors"),
            })

    return {
        "success": True,
        "doctype": doctype,
        "total": len(rows),
        "success_count": success_count,
        "error_count": error_count,
        "created": created,
        "errors": errors,
    }


IMPORT_FORMATS = {
    "csv": import_csv,
    "json": import_json,
    "xlsx": import_excel,
}


def import_docs(doctype: str, fmt: str, content, field_mapping: dict[str, str] | None = None, delimiter: str | None = None) -> dict:
    fmt = fmt.lower()
    if fmt not in IMPORT_FORMATS:
        raise ValueError(f"Unsupported format: {fmt}. Use csv, json, or xlsx.")
    if fmt == "csv":
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        return import_csv(doctype, content, field_mapping, delimiter)
    if fmt == "json":
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        return import_json(doctype, content)
    if fmt == "xlsx":
        if not isinstance(content, bytes):
            raise ValueError("Excel import requires bytes content.")
        return import_excel(doctype, content, field_mapping)
    raise ValueError(f"Unsupported format: {fmt}")


__all__ = ["import_docs", "import_csv", "import_json", "import_excel"]

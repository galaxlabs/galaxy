from galaxy.model.repository import (
    get_portal_permissions_for_doctype,
    get_portal_profile_links,
    get_portal_field_permissions,
)


class PortalPermissionEngine:
    def __init__(self, portal_user: str, portal_role: str):
        self.portal_user = portal_user
        self.portal_role = portal_role
        self._perm_cache: dict[str, dict] = {}
        self._field_perm_cache: dict[str, list] = {}

    def _get_permissions(self, doctype: str) -> dict:
        if doctype not in self._perm_cache:
            perms = get_portal_permissions_for_doctype(self.portal_role, doctype)
            merged = {"read": False, "write": False, "create": False, "delete": False, "permlevel": 0}
            for p in perms:
                for k in ("read", "write", "create", "delete"):
                    if p.get(k):
                        merged[k] = True
                if p.get("permlevel", 0) > merged["permlevel"]:
                    merged["permlevel"] = p["permlevel"]
            self._perm_cache[doctype] = merged
        return self._perm_cache[doctype]

    def can_read(self, doctype: str) -> bool:
        return self._get_permissions(doctype).get("read", False)

    def can_write(self, doctype: str) -> bool:
        return self._get_permissions(doctype).get("write", False)

    def can_create(self, doctype: str) -> bool:
        return self._get_permissions(doctype).get("create", False)

    def can_delete(self, doctype: str) -> bool:
        return self._get_permissions(doctype).get("delete", False)

    def get_owned_docs(self, doctype: str) -> list[dict]:
        links = get_portal_profile_links(self.portal_user)
        return [l for l in links if l["doctype"] == doctype]

    def can_access_doc(self, doctype: str, docname: str) -> bool:
        owned = self.get_owned_docs(doctype)
        return any(d["docname"] == docname for d in owned)

    def get_field_permissions(self, doctype: str) -> list[dict]:
        key = f"{self.portal_role}:{doctype}"
        if key not in self._field_perm_cache:
            all_fp = get_portal_field_permissions(self.portal_role)
            self._field_perm_cache[key] = [fp for fp in all_fp if fp["doctype"] == doctype]
        return self._field_perm_cache[key]

    def get_readable_fields(self, doctype: str) -> list[str] | None:
        fps = self.get_field_permissions(doctype)
        if not fps:
            return None
        return [fp["field_name"] for fp in fps if fp.get("read")]

    def get_writable_fields(self, doctype: str) -> list[str]:
        fps = self.get_field_permissions(doctype)
        if not fps:
            return []
        return [fp["field_name"] for fp in fps if fp.get("write")]


__all__ = ["PortalPermissionEngine"]

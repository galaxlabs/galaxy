import threading
import time
from typing import Any

from galaxy.model.runtimemeta import RuntimeMeta


class MetaCache:
    def __init__(self, default_ttl: int = 300):
        self._lock = threading.Lock()
        self._cache: dict[str, tuple[float, RuntimeMeta]] = {}
        self._default_ttl = default_ttl

    def get(self, key: str) -> RuntimeMeta | None:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            expires_at, meta = entry
            if time.monotonic() > expires_at:
                del self._cache[key]
                return None
            return meta

    def set(self, key: str, meta: RuntimeMeta, ttl: int | None = None) -> None:
        expires_at = time.monotonic() + (ttl if ttl is not None else self._default_ttl)
        with self._lock:
            self._cache[key] = (expires_at, meta)

    def invalidate(self, key: str | None = None) -> None:
        with self._lock:
            if key is None:
                self._cache.clear()
            else:
                self._cache.pop(key, None)

    def invalidate_doctype(self, doctype_name: str) -> None:
        self.invalidate(doctype_name)
        self.invalidate(f"{doctype_name}:crud")
        self.invalidate(f"{doctype_name}:desk")

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._cache)


meta_cache = MetaCache()

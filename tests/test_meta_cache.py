import time
from unittest.mock import MagicMock

from galaxy.model.meta_cache import MetaCache
from galaxy.model.runtimemeta import RuntimeMeta


def _make_meta(name: str = "TestDoc") -> RuntimeMeta:
    return RuntimeMeta(
        doctype={"name": name, "table_name": f"tab{name}"},
        fields=[],
        field_map={},
        permissions=[],
    )


def test_cache_set_and_get():
    cache = MetaCache()
    meta = _make_meta("DocA")
    cache.set("DocA", meta)
    assert cache.get("DocA") is meta


def test_cache_miss():
    cache = MetaCache()
    assert cache.get("NonExistent") is None


def test_cache_invalidate_single():
    cache = MetaCache()
    cache.set("DocA", _make_meta("DocA"))
    cache.set("DocB", _make_meta("DocB"))
    cache.invalidate("DocA")
    assert cache.get("DocA") is None
    assert cache.get("DocB") is not None


def test_cache_invalidate_all():
    cache = MetaCache()
    cache.set("DocA", _make_meta("DocA"))
    cache.set("DocB", _make_meta("DocB"))
    cache.invalidate()
    assert cache.get("DocA") is None
    assert cache.get("DocB") is None


def test_cache_invalidate_doctype():
    cache = MetaCache()
    cache.set("MyDoc", _make_meta("MyDoc"))
    cache.set("MyDoc:crud", _make_meta("MyDoc"))
    cache.set("MyDoc:desk", _make_meta("MyDoc"))
    cache.invalidate_doctype("MyDoc")
    assert cache.get("MyDoc") is None
    assert cache.get("MyDoc:crud") is None
    assert cache.get("MyDoc:desk") is None


def test_cache_ttl_expiry():
    cache = MetaCache(default_ttl=0)
    meta = _make_meta("ExpiryDoc")
    cache.set("ExpiryDoc", meta, ttl=0)
    time.sleep(0.001)
    assert cache.get("ExpiryDoc") is None


def test_cache_size():
    cache = MetaCache()
    assert cache.size == 0
    cache.set("A", _make_meta("A"))
    assert cache.size == 1
    cache.set("B", _make_meta("B"))
    assert cache.size == 2
    cache.invalidate()
    assert cache.size == 0


def test_cache_thread_safety():
    import threading

    cache = MetaCache()
    errors = []

    def worker(n):
        try:
            for i in range(50):
                key = f"Doc{n}-{i}"
                cache.set(key, _make_meta(key))
                cache.get(key)
                cache.invalidate(key)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(errors) == 0

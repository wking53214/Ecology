from plant import SemanticCache

def test_cache_clear_cycle():
    cache = SemanticCache()
    cache.set("key", "value")
    cache.clear()
    assert cache.get("key") is None

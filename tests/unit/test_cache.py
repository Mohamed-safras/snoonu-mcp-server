from src import cache as cache_module
from src.metrics import CACHE_HITS, CACHE_MISSES


def test_cached_avoids_recomputing_on_second_call(fake_redis, monkeypatch):
    monkeypatch.setattr(cache_module, "redis_client", fake_redis)
    calls = []

    @cache_module.cached(ttl_seconds=60)
    def expensive(x):
        calls.append(x)
        return {"value": x * 2}

    label = expensive.__qualname__
    misses_before = CACHE_MISSES.labels(label)._value.get()
    hits_before = CACHE_HITS.labels(label)._value.get()

    assert expensive(3) == {"value": 6}
    assert expensive(3) == {"value": 6}
    assert calls == [3]  # fn only ran once; second call was served from cache

    assert CACHE_MISSES.labels(label)._value.get() == misses_before + 1
    assert CACHE_HITS.labels(label)._value.get() == hits_before + 1


def test_cached_distinguishes_by_arguments(fake_redis, monkeypatch):
    monkeypatch.setattr(cache_module, "redis_client", fake_redis)

    @cache_module.cached(ttl_seconds=60)
    def fn(a, b=1):
        return a + b

    assert fn(1, b=2) == 3
    assert fn(1, b=3) == 4


def test_cached_expires_after_ttl(fake_redis, monkeypatch):
    monkeypatch.setattr(cache_module, "redis_client", fake_redis)
    calls = []

    @cache_module.cached(ttl_seconds=60)
    def fn():
        calls.append(1)
        return "result"

    fn()
    key = next(iter(fake_redis.keys("cache:*")))
    fake_redis.delete(key)  # simulate TTL expiry
    fn()
    assert calls == [1, 1]

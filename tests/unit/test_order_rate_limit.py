import pytest

from src import order_rate_limit as rl
from src.metrics import ORDER_RATE_LIMITED


def test_allows_calls_under_the_limit(fake_redis, monkeypatch):
    monkeypatch.setattr(rl, "redis_client", fake_redis)
    monkeypatch.setattr(rl, "MAX_PER_HOUR", 3)

    rl.check_rate_limit()
    rl.check_rate_limit()
    rl.check_rate_limit()  # 3rd call still within the limit, must not raise


def test_blocks_calls_over_the_limit(fake_redis, monkeypatch):
    monkeypatch.setattr(rl, "redis_client", fake_redis)
    monkeypatch.setattr(rl, "MAX_PER_HOUR", 2)
    before = ORDER_RATE_LIMITED._value.get()

    rl.check_rate_limit()
    rl.check_rate_limit()
    with pytest.raises(rl.OrderRateLimitError):
        rl.check_rate_limit()

    assert ORDER_RATE_LIMITED._value.get() == before + 1


def test_counter_key_has_an_hour_expiry(fake_redis, monkeypatch):
    monkeypatch.setattr(rl, "redis_client", fake_redis)

    rl.check_rate_limit()

    ttl = fake_redis.ttl(rl._KEY)
    assert 0 < ttl <= 3600

import pytest
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from src import order_rate_limit as rl
from src.api.exceptions import ProductNotFoundError
from src.client import client
from src.tools import orders as orders_tool
from tests.conftest import call_tool

CART_ARGS = {
    "cart": [{"product_id": "p1", "quantity": 2}],
    "recipient": {"name": "A"},
    "delivery": {"city": "Doha"},
    "sender": {"name": "B"},
}


def _build_mcp():
    mcp = FastMCP("test")
    orders_tool.register(mcp)
    return mcp


def test_create_order_happy_path(monkeypatch, fake_redis):
    monkeypatch.setattr(rl, "redis_client", fake_redis)
    monkeypatch.setattr(client.products, "get_price", lambda product_id: 25.0)
    created = {}
    monkeypatch.setattr(
        client.orders, "create", lambda ref, total, *a, **k: created.update(ref=ref, total=total)
    )

    out = call_tool(_build_mcp(), "snoonu_create_order", CART_ARGS)

    assert out["order_ref"].startswith("SNU-")
    assert out["total"] == {"amount": 50.0, "currency": "QAR"}
    assert created == {"ref": out["order_ref"], "total": 50.0}


def test_create_order_unknown_product_becomes_value_error(monkeypatch, fake_redis):
    monkeypatch.setattr(rl, "redis_client", fake_redis)

    def boom(product_id):
        raise ProductNotFoundError(product_id)

    monkeypatch.setattr(client.products, "get_price", boom)

    with pytest.raises(ToolError) as exc_info:
        call_tool(_build_mcp(), "snoonu_create_order", CART_ARGS)
    assert isinstance(exc_info.value.__cause__, ValueError)


def test_create_order_blocked_after_rate_limit(monkeypatch, fake_redis):
    monkeypatch.setattr(rl, "redis_client", fake_redis)
    monkeypatch.setattr(rl, "MAX_PER_HOUR", 1)
    monkeypatch.setattr(client.products, "get_price", lambda product_id: 10.0)
    monkeypatch.setattr(client.orders, "create", lambda *a, **k: None)

    mcp = _build_mcp()
    call_tool(mcp, "snoonu_create_order", CART_ARGS)  # 1st: within limit

    with pytest.raises(ToolError) as exc_info:
        call_tool(mcp, "snoonu_create_order", CART_ARGS)  # 2nd: blocked
    assert isinstance(exc_info.value.__cause__, rl.OrderRateLimitError)


def test_track_order_not_found(monkeypatch):
    monkeypatch.setattr(client.orders, "get", lambda order_id: None)
    out = call_tool(_build_mcp(), "snoonu_track_order", {"order_number": "SNU-XXXXXX"})
    assert out["status"] == "not_found"


def test_track_order_pending_payment(monkeypatch):
    from datetime import datetime, timezone

    monkeypatch.setattr(
        client.orders,
        "get",
        lambda order_id: {
            "status": "pending_payment",
            "total_amount": 50.0,
            "currency": "QAR",
            "created_at": datetime.now(timezone.utc),
        },
    )
    out = call_tool(_build_mcp(), "snoonu_track_order", {"order_number": "SNU-AAAAAA"})
    assert out == {"status": "pending_payment", "total": 50.0, "currency": "QAR"}

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from src.client import client

pytestmark = pytest.mark.integration


def test_create_then_get_roundtrip():
    ref = f"TEST-{uuid.uuid4().hex[:8]}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=45)

    client.orders.create(
        ref, 42.5, "QAR",
        recipient={"name": "Test Recipient"},
        delivery={"city": "Doha"},
        sender={"name": "Test Sender"},
        gift_message=None,
        expires_at=expires_at,
        cart=[],
    )

    order = client.orders.get(ref)
    assert order is not None
    assert order["status"] == "pending_payment"
    assert order["total_amount"] == 42.5
    assert order["currency"] == "QAR"

def test_get_unknown_order_returns_none():
    assert client.orders.get("does-not-exist") is None

def test_create_with_cart_items_does_not_violate_fk():
    # Regression: order_items has no ORM relationship() to Order, so without an
    # explicit flush between the two inserts, SQLAlchemy can emit the order_items
    # insert before the parent orders insert and trip the FK constraint.
    ref = f"TEST-{uuid.uuid4().hex[:8]}"
    client.orders.create(
        ref, 10.0, "QAR",
        recipient={}, delivery={}, sender={}, gift_message=None,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=45),
        cart=[{"product_id": "snu-00001", "quantity": 1}],
    )
    assert client.orders.get(ref) is not None

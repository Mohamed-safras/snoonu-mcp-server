import random
import string
from datetime import datetime, timedelta, timezone
from src.client import client
from src.api.exceptions import ProductNotFoundError
from src.order_rate_limit import check_rate_limit
from src.activity_log import log_order_event
from src.metrics import ORDERS_CREATED, instrument_tool

def _new_ref() -> str:
    return "SNU-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

def register(mcp):
    @mcp.tool(name="snoonu_create_order")
    @instrument_tool("snoonu_create_order")
    def create_order(cart: list[dict], recipient: dict, delivery: dict,
                      sender: dict, gift_message: str | None = None, currency: str = "QAR") -> dict:
        check_rate_limit()
        ref = _new_ref()
        total = 0.0
        for item in cart:
            try:
                price = client.products.get_price(item["product_id"])
            except ProductNotFoundError as exc:
                raise ValueError(str(exc))
            total += price * item["quantity"]

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=45)
        client.orders.create(ref, total, currency, recipient, delivery, sender,
                              gift_message, expires_at, cart)
        log_order_event(ref, "created", total)
        ORDERS_CREATED.inc()

        return {"order_ref": ref, "pay_url": f"https://your-next-app.example.com/pay/{ref}",
                "total": {"amount": total, "currency": currency}, "expires_at": expires_at.isoformat()}

    @mcp.tool(name="snoonu_track_order")
    @instrument_tool("snoonu_track_order")
    def track_order(order_number: str) -> dict:
        row = client.orders.get(order_number)
        if not row:
            return {"status": "not_found"}
        elapsed_min = (datetime.now(timezone.utc) - row["created_at"]).total_seconds() / 60
        stages = ["pending_payment", "paid", "preparing", "out_for_delivery", "delivered"]
        idx = min(int(elapsed_min // 2), len(stages) - 1)
        status = row["status"] if row["status"] == "pending_payment" else stages[max(idx, 1)]
        return {"status": status, "total": row["total_amount"], "currency": row["currency"]}

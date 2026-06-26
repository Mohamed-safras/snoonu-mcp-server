import logging

logger = logging.getLogger("snoonu_mcp.activity")
logging.basicConfig(level=logging.INFO)

def log_order_event(order_ref: str, event: str, total: float | None = None) -> None:
    logger.info("order=%s event=%s total=%s", order_ref, event, total)

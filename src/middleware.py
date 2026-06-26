import logging
import time

logger = logging.getLogger("snoonu_mcp.requests")

def log_request(method: str, path: str, start: float) -> None:
    logger.info("%s %s — %.1fms", method, path, (time.time() - start) * 1000)

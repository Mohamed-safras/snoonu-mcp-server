import time
import os

_timestamps: list[float] = []
MAX_PER_HOUR = int(os.environ.get("SNOONU_ORDER_MAX_PER_HOUR", "25"))

class OrderRateLimitError(Exception):
    pass

def check_rate_limit() -> None:
    now = time.time()
    cutoff = now - 3600
    while _timestamps and _timestamps[0] < cutoff:
        _timestamps.pop(0)
    if len(_timestamps) >= MAX_PER_HOUR:
        raise OrderRateLimitError("Too many orders this hour — try again later.")
    _timestamps.append(now)

import time
from functools import wraps

def cached(ttl_seconds: int):
    """Simple per-argument TTL cache for read-mostly tool handlers."""
    def decorator(fn):
        store: dict = {}
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            entry = store.get(key)
            if entry and time.time() - entry[1] < ttl_seconds:
                return entry[0]
            result = fn(*args, **kwargs)
            store[key] = (result, time.time())
            return result
        return wrapper
    return decorator
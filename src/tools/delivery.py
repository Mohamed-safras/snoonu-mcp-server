import math
from datetime import datetime, timezone
from src.client import client
from src.metrics import instrument_tool

SNOONU_HQ = (25.3548, 51.4326)  # West Bay / Lusail, Doha — illustrative only

def _haversine_km(lat1, lng1, lat2, lng2):
    R = 6371
    dlat, dlng = math.radians(lat2 - lat1), math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))

def _tier(km: float) -> tuple[str, int]:
    if km <= 10: return "Same day", 0
    if km <= 30: return "Same day / next day", 1
    if km <= 55: return "Next day", 2
    return "1-2 days", 3

def register(mcp):
    @mcp.tool(name="snoonu_list_delivery_cities")
    @instrument_tool("snoonu_list_delivery_cities")
    def list_delivery_cities(query: str | None = None, limit: int = 8) -> dict:
        rows = client.cities.list(query)
        sliced = rows[:limit]
        return {"cities": [{"name": row["name"], "aliases": row["aliases"]} for row in sliced],
                "total_matched": len(rows), "showing": len(sliced)}

    @mcp.tool(name="snoonu_check_delivery")
    @instrument_tool("snoonu_check_delivery")
    def check_delivery(city: str, delivery_date: str | None = None, product_id: str | None = None) -> dict:
        row = client.cities.get(city)
        if not row:
            return {"city": city, "now": datetime.now(timezone.utc).isoformat(),
                    "checked_date": delivery_date or "today", "available": False,
                    "rate": 0, "currency": "QAR", "perishable_warning": "City not found"}
        km = _haversine_km(*SNOONU_HQ, row["lat"], row["lng"])
        eta, tier = _tier(km)
        return {"city": city, "now": datetime.now(timezone.utc).isoformat(),
                "checked_date": delivery_date or "today", "available": True,
                "rate": 10 + tier * 5, "currency": "QAR", "perishable_warning": None,
                "eta_label": eta}

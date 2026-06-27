import pytest
from mcp.server.fastmcp import FastMCP

from src.client import client
from src.tools import delivery as delivery_tool
from src.tools.delivery import _haversine_km, _tier
from tests.conftest import call_tool


def _build_mcp():
    mcp = FastMCP("test")
    delivery_tool.register(mcp)
    return mcp


def test_haversine_zero_distance():
    assert _haversine_km(25.35, 51.43, 25.35, 51.43) == pytest.approx(0.0, abs=1e-6)


def test_haversine_known_distance_doha_to_wakrah():
    km = _haversine_km(25.2854, 51.5310, 25.1659, 51.6038)
    assert 10 < km < 20


@pytest.mark.parametrize(
    "km,expected_label,expected_tier",
    [
        (5, "Same day", 0),
        (20, "Same day / next day", 1),
        (40, "Next day", 2),
        (100, "1-2 days", 3),
    ],
)
def test_tier_boundaries(km, expected_label, expected_tier):
    label, tier = _tier(km)
    assert label == expected_label
    assert tier == expected_tier


def test_check_delivery_unknown_city_returns_unavailable(monkeypatch):
    monkeypatch.setattr(client.cities, "get", lambda name: None)
    out = call_tool(_build_mcp(), "snoonu_check_delivery", {"city": "Nowhere"})
    assert out["available"] is False
    assert out["perishable_warning"] == "City not found"


def test_check_delivery_known_city_returns_eta(monkeypatch):
    monkeypatch.setattr(
        client.cities, "get", lambda name: {"name": name, "lat": 25.2854, "lng": 51.5310, "aliases": []}
    )
    out = call_tool(_build_mcp(), "snoonu_check_delivery", {"city": "Doha"})
    assert out["available"] is True
    assert out["eta_label"]


def test_list_delivery_cities_respects_limit(monkeypatch):
    rows = [{"name": f"City{i}", "aliases": []} for i in range(20)]
    monkeypatch.setattr(client.cities, "list", lambda query: rows)
    out = call_tool(_build_mcp(), "snoonu_list_delivery_cities", {"limit": 5})
    assert out["showing"] == 5
    assert out["total_matched"] == 20
    assert len(out["cities"]) == 5

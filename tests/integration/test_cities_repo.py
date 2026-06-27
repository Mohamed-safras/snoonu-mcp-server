import pytest
from src.client import client

pytestmark = pytest.mark.integration


def test_list_finds_seeded_city():
    cities = client.cities.list("Doha")
    assert any(c["name"] == "Doha" for c in cities)

def test_get_unknown_city_returns_none():
    assert client.cities.get("Nowhereville") is None

def test_get_known_city_returns_coordinates():
    city = client.cities.get("Doha")
    assert city is not None
    assert -90 <= city["lat"] <= 90
    assert -180 <= city["lng"] <= 180

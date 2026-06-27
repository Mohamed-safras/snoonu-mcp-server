import pytest
from src.client import client

pytestmark = pytest.mark.integration


def test_search_finds_seeded_product():
    results = client.products.search("rose", None, None, None, 5)
    assert len(results) > 0
    assert all(r["price_currency"] == "QAR" for r in results)

def test_get_unknown_product_returns_none():
    assert client.products.get("does-not-exist") is None

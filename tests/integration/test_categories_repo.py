import pytest
from src.client import client

pytestmark = pytest.mark.integration


def test_list_all_returns_seeded_categories():
    categories = client.categories.list_all()
    assert len(categories) > 0
    assert all(isinstance(name, str) and isinstance(slug, str) for name, slug in categories)

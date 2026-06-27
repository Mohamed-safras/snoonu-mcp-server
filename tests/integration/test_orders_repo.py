import pytest
from src.client import client
from src.api.exceptions import ProductNotFoundError

pytestmark = pytest.mark.integration


def test_get_price_raises_for_unknown_product():
    with pytest.raises(ProductNotFoundError):
        client.products.get_price("does-not-exist")

"""
Composition root for the catalog/order data-access layer. `tools/`
modules import `client` from here and never touch Postgres directly.
Swap-in point for a real Snoonu API later: implement `base.CatalogClient`
against HTTP and change only the assignment below.
"""
from src.api.client import DatabaseCatalogClient
from src.api.base import CatalogClient

client: CatalogClient = DatabaseCatalogClient()
# Architecture

snoonu-mcp is a FastMCP server exposing 7 tools (snoonu_search_products,
snoonu_get_product, snoonu_list_categories, snoonu_list_delivery_cities,
snoonu_check_delivery, snoonu_create_order, snoonu_track_order) over the
Streamable HTTP transport.

Layers:

- `tools/` — MCP tool definitions. Depend only on `api.client.client`.
- `api/base.py` — interfaces (ports) the tools depend on.
- `api/postgres/` — the only current adapter (implements the ports against
  Postgres). A future real-API adapter would live alongside this and get
  swapped in via `api/client.py` without touching `tools/`.
- `order_rate_limit.py`, `cache.py`, `activity_log.py` — cross-cutting
  concerns, independent of storage backend.

This is mock data (`scripts/seed.py`), not a live Snoonu integration.
Grocery/Market product images and names courtesy of Open Food Facts
(https://openfoodfacts.org), used under CC-BY-SA 3.0 / ODbL.

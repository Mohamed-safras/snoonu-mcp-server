from src.client import client
from src.cache import cached
from src.metrics import instrument_tool

def register(mcp):
    @mcp.tool(name="snoonu_list_categories")
    @instrument_tool("snoonu_list_categories")
    @cached(ttl_seconds=300)
    def list_categories(depth: int = 1) -> dict:
        rows = client.categories.list_all()
        return {"categories": [{"name": name, "url": f"/category/{slug}"} for name, slug in rows]}
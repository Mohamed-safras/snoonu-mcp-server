from src.api.client import client
from src.cache import cached

def register(mcp):
    @mcp.tool(name="snoonu_list_categories")
    @cached(ttl_seconds=300)
    def list_categories(depth: int = 1) -> dict:
        rows = client.categories.list_all()
        return {"categories": [{"name": name, "url": f"/category/{slug}"} for name, slug in rows]}
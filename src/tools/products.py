from src.client import client
from src.metrics import instrument_tool

def register(mcp):
    @mcp.tool(name="snoonu_search_products")
    @instrument_tool("snoonu_search_products")
    def search_products(q:str,
                        currency:str = "QAR", 
                        limit: int =24,
                        category:str | None = None, 
                        min_price:float | None = None, 
                        max_price:float | None = None
                        ) -> dict:
        rows = client.products.search(q, category, min_price, max_price, min(limit, 50))
        return {"results": [_to_search_item(row) for row in rows]}
    
    @mcp.tool(name="snoonu_get_product")
    @instrument_tool("snoonu_get_product")
    def get_product(product_id: str, currency: str = "QAR") -> dict | None:
        row = client.products.get(product_id)
        if not row:
            return None
        item = _to_search_item(row)
        item["description"] = row.get("description")
        item["images"] = row.get("images") or ([row["image_url"]] if row.get("image_url") else [])
        return item

def _to_search_item(row: dict) -> dict:
    return {
        "id": row["id"], 
        "name": row["name"], 
        "summary": row["summary"],
        "price": {"amount": float(row["price_amount"]), "currency": row["price_currency"]},
        "compare_at_price": ({"amount": float(row["compare_at_amount"]), 
                              "currency": row["price_currency"]}
                              if row.get("compare_at_amount") else None),
        "in_stock": row["in_stock"], 
        "image_url": row.get("image_url"),
        "rating": row.get("rating"),
        "category": {"name": row["category_name"], "slug": row["category_slug"]},
    }
from mcp.server.fastmcp import FastMCP
from src.tools import products, categories, delivery, orders

mcp = FastMCP("snoonu-mcp-server")

products.register(mcp)
categories.register(mcp)
delivery.register(mcp)
orders.register(mcp)

app = mcp.streamable_http_app()

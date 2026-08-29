"""MCP tool server for ShopPilot AI agents.

This server exposes only controlled business operations. It never exposes a
database connection or arbitrary SQL to an LLM.
"""

from mcp.server.fastmcp import FastMCP

from .core.database import SessionLocal
from .services.catalog import get_product, search_products

mcp = FastMCP("ShopPilot AI Tools")


@mcp.tool()
def search_catalog(query: str, limit: int = 5) -> list[dict[str, object]]:
    """Find active products by name. Prices and details come only from SQL Server."""
    db = SessionLocal()
    try:
        return search_products(db, query, limit)
    finally:
        db.close()


@mcp.tool()
def product_details(product_id: int) -> dict[str, object]:
    """Return the current catalog record for one active product."""
    db = SessionLocal()
    try:
        product = get_product(db, product_id)
        return product or {"error": "Product not found."}
    finally:
        db.close()


if __name__ == "__main__":
    mcp.run()

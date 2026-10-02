from fastmcp import FastMCP
from ai_engineer.mcp_server.tools.search_internet import search_internet as _search_internet

mcp = FastMCP("My Simple Server")

@mcp.tool()
def search_internet(query: str) -> list[dict]:
    """Search the internet for a given query.

    Return the top 3 results as a list of dicts with keys:
    - url: URL of the article
    - content: Full text content extracted from the article

    Example output format:
    [
        {"url": "https://example.com", "content": "Article text..."},
        {"url": "https://example2.com", "content": "Article text 2..."},
        {"url": "https://example3.com", "content": "Article text 3..."}
    ]
    """
    return _search_internet(query)

@mcp.tool()
def get_news_from_db(query: str) -> str:
    """Get news from the database."""
    return f"Retrieving news from the database for {query}."

@mcp.tool()
def get_financial_data(stock_id: str) -> str:
    """Get financial data from the database."""
    return f"Retrieving financial data from the database for {stock_id}."

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Return a personalized greeting resource."""
    return f"Hello, {name}! Welcome to your local MCP server."

if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=7000)
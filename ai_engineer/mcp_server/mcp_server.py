from fastmcp import FastMCP

mcp = FastMCP("My Simple Server")

@mcp.tool()
def search_internet(query: str) -> str:
    """Search the internet for a given query."""
    return f"Searching the internet for {query}."

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
    mcp.run(transport="sse", host="127.0.0.1", port=8000)
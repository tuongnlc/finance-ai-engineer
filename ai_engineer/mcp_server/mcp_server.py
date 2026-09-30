from fastmcp import FastMCP

mcp = FastMCP("My Simple Server")


@mcp.tool()
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    return a + b


@mcp.tool()
def get_current_weather(location: str) -> str:
    """Get the current weather for a given location."""
    if "tokyo" in location.lower():
        return "The weather in Tokyo is 15°C and sunny."
    return f"The weather in {location} is 22°C and partly cloudy."


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Return a personalized greeting resource."""
    return f"Hello, {name}! Welcome to your local MCP server."


if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8000)
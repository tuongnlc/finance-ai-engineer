from fastmcp import FastMCP
from ai_engineer.mcp_server.tools.search_internet import search_internet as _search_internet
from ai_engineer.mcp_server.tools.search_newspaper_db import SearchNewsPaperDB

import os
from dotenv import load_dotenv
load_dotenv()


llm_api_key = os.getenv("LLM_CHAT_API_KEY_1")

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
async def retrieve_newspaper_db(query: str, stock_id: str = None, main_topic: str=None) -> list[dict]:
    """
        Get newspaper from the newspaper collection in Qdrant.
    
        Args:
            query: The query to search for.
            stock_id: The stock ID to filter the search.
            main_topic: The main topic to filter the search.
        
        Returns:
            A list of dicts with keys:
            - newspaper_title: Title of the newspaper
            - publish_date: Date of the newspaper
            - newspaper_content: Full text content extracted from the newspaper
        
        Example Ouput format:
            [
                {"newspaper_title": "Tin tức thị trường gần đây về ngân hàng ACB", "publish_date": "2024-01-01", "newspaper_content": "thị trường & giao dịch"},
                {"newspaper_title": "Tin tức thị trường gần đây về ngân hàng ACB", "publish_date": "2024-01-02", "newspaper_content": "Tin tức thị trường gần đây về ngân hàng ACB, bao gồm thông tin về giao dịch, thao tác, tham gia, v.v.""}
            ]
    """
    if stock_id is not None or not "null" or not "none":
        filter = {"stocks_mention": stock_id.lower()}
    else:
        filter = {}

    search_news_paper_db = SearchNewsPaperDB(
        sparse_model_name="Qdrant/bm25",
        sparse_vector_name="bm25_sparse",
        dense_model_name="gemini-embedding-2",
        dense_vector_name="gemini_dense_vector",
        collection_name="newspaper_embedded",
        dense_api_key=llm_api_key,
        query_filter=filter,
    )

    dense_hit = await search_news_paper_db.retrieve_database_with_user_query(
        query=query,
        limit=3,
        search_type="dense",
    )
    return dense_hit


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
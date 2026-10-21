import asyncio
from ai_engineer.mcp_server.tools.search_newspaper_db import SearchNewsPaperDB
import os
from dotenv import load_dotenv

from ai_engineer.shared.llm.create_llm import create_gemini_llm
load_dotenv()


llm_api_key = os.getenv("LLM_CHAT_API_KEY_1")


van_ban_khong_dau = 'doanh thu hoat dong kinh doanh ACB'

llm = create_gemini_llm(
    api_key=llm_api_key,
    model_name="gemini-3.1-flash-lite",
    temperature=0,
)

search_news_paper_db = SearchNewsPaperDB(
        sparse_model_name="Qdrant/bm25",
        sparse_vector_name="bm25_sparse",
        dense_model_name="gemini-embedding-2",
        dense_vector_name="gemini_dense_vector",
        collection_name="newspaper_embedded",
        dense_api_key=llm_api_key,
        query_filter=filter,
    )

async def main():
    dense_hit = await search_news_paper_db.retrieve_database_with_user_query(
    query=van_ban_khong_dau,
    limit=3,
    search_type="Thông tin thị trường đáng chú ý hôm nay",
)
    print(dense_hit)

if __name__ == "__main__":
    asyncio.run(main())
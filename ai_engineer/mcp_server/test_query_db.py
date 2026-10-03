
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from qdrant_client import QdrantClient
from tools.search_newspaper_db import SearchNewsPaperDB
import os
from dotenv import load_dotenv
load_dotenv()


llm_api_key = os.getenv("LLM_CHAT_API_KEY_1")

{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "response": "original_query='Tin tuc thi truong gan day ve ngan hang ACB' vietnamese_with_diacritics='Tin tức thị trường gần đây về ngân hàng ACB' question_type='tin tức thị trường' main_topic='thị trường & giao dịch' stock_id='ACB' target_year='2026' document_type='other' optimized_search_query=['tin tức thị trường gần đây về ngân hàng ACB', 'biến động thị trường và cổ phiếu ACB mới nhất', 'thông tin giao dịch và thị trường ngân hàng ACB']"
}

# need tool get_news_from_db
query = "Tin tức thị trường gần đây về ngân hàng ACB"

qdrant_client = QdrantClient(url="http://localhost:6333", timeout=600)

document_search_service = SearchNewsPaperDB(
    qdrant_client,
    sparse_model_name="Qdrant/bm25",
    sparse_vector_name="bm25_sparse",
    dense_model_name="gemini-embedding-2",
    dense_vector_name="gemini_dense_vector",
    collection_name="newspaper_embedded",
    dense_api_key=llm_api_key,
    query_filter={
        "stocks_mention": "",
    },
)

async def test_dense_search():
    dense_hit = await document_search_service.retrieve_database_with_user_query(
        query=query,
        limit=3,
        search_type="dense",
    )
    # print(dense_hit)
    return dense_hit

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(test_dense_search())
    print(result)
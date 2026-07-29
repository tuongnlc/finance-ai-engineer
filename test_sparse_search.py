# from qdrant_client.models import , Fusion

#Convert Vietnamese without diacritics to Vietnamese with diacritics
from qdrant_client import QdrantClient, models
from ai_engineer.applications.chatbot.service.rag_service import DocumentSearchService
from ai_engineer.shared.llm.create_llm import create_gemini_embedding, create_gemini_llm

import os
from dotenv import load_dotenv
load_dotenv()


llm_api_key = os.getenv("LLM_CHAT_API_KEY_1")


van_ban_khong_dau = 'doanh thu hoat dong kinh doanh ACB'

llm = create_gemini_llm(
    api_key=llm_api_key,
    model_name="gemini-3.1-flash-lite",
    temperature=0,
)

from langchain_core.prompts import ChatPromptTemplate

llm.invoke("Chuyen tu tieng viet thanh co dau")

prompt_template = ChatPromptTemplate.from_messages([
        (
            "system", """You are a machine translate machine. Your job is convert from Vietnamese without diacritics to Vietnamese with diacritics. 
                        You don't need to add any punctuation marks.
                        If user input Vietnamese with diacritics do nothing. return original text.
                        If user input is not Vietnamese, return original text.
                        """
        ),
        ("user", "{text}")
    ])

chain = prompt_template | llm


response = chain.invoke({
            "text": van_ban_khong_dau
        })

response = response.content[0].get("text")
print("tieng viet co dau")
print(response)

primary_filter = models.Filter(
    must=[
        models.FieldCondition(
            key="document_type",
            match=models.MatchValue(value="income_statement")
        )
    ]
)




# query qdrant db
qdrant_client = QdrantClient(url="http://localhost:6333", timeout=600)

# document_search_service = DocumentSearchService(
#     qdrant_client,
#     sparse_model_name="Qdrant/bm25",
#     sparse_vector_name="bm25_sparse",
#     dense_model_name="gemini-embedding-2",
#     dense_vector_name="gemini_dense_vector",
#     collection_name="stock_price_embedded",
#     dense_api_key=llm_api_key,
# )

# hydrid_hit = document_search_service.simlar_search_with_sparse_vector(
#     query=response,
#     limit=20
# )

# print(hydrid_hit)


from qdrant_client import QdrantClient
from qdrant_client.models import Prefetch, Filter, FieldCondition, MatchValue

client = QdrantClient("http://localhost:6333")

# 1. Định nghĩa Filter ưu tiên hàng đầu (Báo cáo KQKD)
primary_filter = Filter(
    must=[
        FieldCondition(
            key="document_type",
            match=MatchValue(value="income_statement")
        )
    ]
)
from fastembed import SparseTextEmbedding
from qdrant_client.models import Prefetch, Filter, FieldCondition, MatchValue, FusionQuery, Fusion, SparseVector
from underthesea import word_tokenize

sparse_embedding = SparseTextEmbedding(model_name="Qdrant/bm25",  disable_stemmer=True)
tokens = word_tokenize(response, format="text")
sparse_vector_obj = next(sparse_embedding.embed([tokens]))
sparse_vector = SparseVector(
    indices=sparse_vector_obj.indices.tolist(),
    values=sparse_vector_obj.values.tolist()
)

# 2. Truy vấn theo cấp bậc ưu tiên
search_response = client.query_points(
    collection_name="stock_price_embedded",
    prefetch=[
        # Bước 1: Ép Qdrant chỉ tìm trong Báo cáo KQKD trước
        Prefetch(
            query=sparse_vector,
            using="bm25_sparse",
            filter=primary_filter,
            limit=10,
        ),
        # Bước 2: Dự phòng - nếu Bước 1 không đủ hoặc trống, quét toàn bộ collection
        Prefetch(
            query=sparse_vector,
            using="bm25_sparse",
            limit=10,
        )
    ],
    query=FusionQuery(fusion=Fusion.RRF),
    limit=10
)

print(search_response)
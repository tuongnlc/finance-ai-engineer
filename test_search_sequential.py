import asyncio
from qdrant_client import QdrantClient, models
from ai_engineer.applications.chatbot.service.rag_service import DocumentSearchService
from ai_engineer.shared.llm.create_llm import create_gemini_embedding, create_gemini_llm

import os
from dotenv import load_dotenv
load_dotenv()


llm_api_key = os.getenv("LLM_CHAT_API_KEY_1")


van_ban_khong_dau = 'Doanh thu ngan hang ACB'

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

qdrant_client = QdrantClient(url="http://localhost:6333", timeout=600)

from time import time
start_time = time()
#search newspaper
document_search_service = DocumentSearchService(
    qdrant_client,
    sparse_model_name="Qdrant/bm25",
    sparse_vector_name="bm25_sparse",
    dense_model_name="gemini-embedding-2",
    dense_vector_name="gemini_dense_vector",
    collection_name="newspaper_embedded",
    dense_api_key=llm_api_key,
)

# search finance document
document_search_service = DocumentSearchService(
    qdrant_client,
    sparse_model_name="Qdrant/bm25",
    sparse_vector_name="bm25_sparse",
    dense_model_name="gemini-embedding-2",
    dense_vector_name="gemini_dense_vector",
    collection_name="stock_price_embedded",
    dense_api_key=llm_api_key,
)


async def main():
    results = await document_search_service.retrieve_database_with_user_query(
    query=response,
    limit=20
)
    print(results)
# print(hydrid_hit)

if __name__ == "__main__":
    asyncio.run(main())




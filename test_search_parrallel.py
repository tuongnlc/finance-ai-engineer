import os
from concurrent.futures import ThreadPoolExecutor
from time import time

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from qdrant_client import QdrantClient

from ai_engineer.applications.chatbot.service.rag_service import DocumentSearchService
from ai_engineer.shared.llm.create_llm import create_gemini_llm

load_dotenv()


llm_api_key = os.getenv("LLM_CHAT_API_KEY_1")

van_ban_khong_dau = "Doanh thu ngan hang ACB"

llm = create_gemini_llm(
    api_key=llm_api_key,
    model_name="gemini-3.1-flash-lite",
    temperature=0,
)

llm.invoke("Chuyen tu tieng viet thanh co dau")

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a machine translate machine. Your job is convert from Vietnamese without diacritics to Vietnamese with diacritics.
                        You don't need to add any punctuation marks.
                        If user input Vietnamese with diacritics do nothing. return original text.
                        If user input is not Vietnamese, return original text.
                        """,
        ),
        ("user", "{text}"),
    ]
)

chain = prompt_template | llm

response = chain.invoke({"text": van_ban_khong_dau})
response = response.content[0].get("text")

print("tieng viet co dau")
print(response)

qdrant_client = QdrantClient(url="http://localhost:6333", timeout=600)

collections = {
    "newspaper_embedded": "newspaper",
    "stock_price_embedded": "stock_price",
}

search_services = {
    collection_name: DocumentSearchService(
        qdrant_client,
        sparse_model_name="Qdrant/bm25",
        sparse_vector_name="bm25_sparse",
        dense_model_name="gemini-embedding-2",
        dense_vector_name="gemini_dense_vector",
        collection_name=collection_name,
        dense_api_key=llm_api_key,
    )
    for collection_name in collections
}


def search_collection(collection_name: str, query: str, limit: int = 20):
    document_search_service = search_services[collection_name]
    return document_search_service.simlar_search_with_dense_vector(
        query=query,
        limit=limit,
    )


start_time = time()

with ThreadPoolExecutor(max_workers=len(collections)) as executor:
    future_map = {
        alias: executor.submit(search_collection, collection_name, response, 20)
        for collection_name, alias in collections.items()
    }
    search_results = {
        alias: future.result()
        for alias, future in future_map.items()
    }

end_time = time()

print("newspaper result")
print(search_results["newspaper"])
print("stock_price result")
print(search_results["stock_price"])
print(f"Search time: {end_time - start_time}")

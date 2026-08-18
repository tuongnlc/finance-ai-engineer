# from qdrant_client.models import , Fusion

#Convert Vietnamese without diacritics to Vietnamese with diacritics
from qdrant_client import QdrantClient, models
from ai_engineer.applications.chatbot.service.rag_service import DocumentSearchService
from ai_engineer.shared.llm.create_llm import create_gemini_embedding, create_gemini_llm

DocumentSearchService

import os
from dotenv import load_dotenv
load_dotenv()


llm_api_key = os.getenv("LLM_CHAT_API_KEY_1")


van_ban_khong_dau = 'No xau ngan hang ACB'

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

# query qdrant db
qdrant_client = QdrantClient(url="http://localhost:6333", timeout=600)

document_search_service = DocumentSearchService(
    qdrant_client,
    sparse_model_name="Qdrant/bm25",
    sparse_vector_name="bm25_sparse",
    dense_model_name="gemini-embedding-2",
    dense_vector_name="gemini_dense_vector",
    collection_name="stock_price_embedded",
    dense_api_key=llm_api_key,
)

dense_hit = document_search_service.simlar_search_with_dense_vector(
    query=response,
    limit=20
)

# print(type(dense_hit))

print(len(dense_hit.points)) #return 20 points

# print("-----------------")
# print("")
# for hit in dense_hit:
# #     # print(hit.payload)
#     # print(hit.points)
#     print(hit)
# #     break

# print("-----------------")
# print("")

for point in dense_hit.points:
    print(point.payload)
    print(" ")
#     break

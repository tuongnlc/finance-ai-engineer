from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import QdrantClient

import os
from dotenv import load_dotenv

load_dotenv()

llm_api_key_1 = os.getenv("LLM_CHAT_API_KEY_1")
temperature = 0.

client = QdrantClient(url="http://localhost:6333")
collection_name = "newspaper_embedded"


def scroll_database(target_ids):
    target_ids = [str(x) for x in target_ids]

    points = client.retrieve(
        collection_name="newspaper",
        ids=target_ids,
        with_payload=True,
        with_vectors=False,
    )

    titles = []
    newspaper_content = []

    for point in points:
        # print(point.payload["id"])
        titles.append(point.payload["newspaper_title"])
        newspaper_content.append(point.payload["newspaper_content"])
    return titles, newspaper_content

def search_semantic(user_query: str, top_k: int = 5, fetch_k: int = 50) -> list[str]:
    embeddings = GoogleGenerativeAIEmbeddings(
    google_api_key=llm_api_key_1,
    model="gemini-embedding-2",
    output_dimensionality=768
)
    vector = embeddings.embed_query(user_query)

    search_result = client.query_points(
        collection_name=collection_name,
        query=vector,            
        limit=fetch_k,
        with_payload=True,             
        with_vectors=False             
     )

    output_points = []
    seen = set()

    for point in search_result.points:
        doc_id = (point.payload or {}).get("document_id")
        if doc_id is None:
            continue

        doc_id = str(doc_id)
        if doc_id in seen:
            continue

        seen.add(doc_id)
        output_points.append(doc_id)

        if len(output_points) >= top_k:
            break

    return output_points


test_similar_search = search_semantic("What is the latest news about ACB?")
print(test_similar_search)
titles, newspaper_content = scroll_database(test_similar_search)
output_ = {}
for i in zip(titles, newspaper_content):
    output_[i[0]] = i[1]
# print(output_)
# output_[i[0]]
# output_[i[1]]
# print(titles)
print(output_)

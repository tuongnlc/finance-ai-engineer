from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchAny


client = QdrantClient(url="http://localhost:6333")
collection_name = "newspaper_embedded"


def scroll_database(target_ids):
    target_ids = [str(x) for x in target_ids]

    query_filter = Filter(
        must=[
            FieldCondition(
                key="id",
                match=MatchAny(any=target_ids),
            )
        ]
    )
    filtered_points = []
    next_offset = None

    while True:
        points, next_offset = client.scroll(
            collection_name="newspaper",
            scroll_filter=query_filter,
            limit=256,
            offset=next_offset,
            with_payload=True,
            with_vectors=False,
        )

        if not points:
            break

        filtered_points.extend(points)

        if next_offset is None:
            break

    titles = []

    for point in filtered_points:
        print(point.payload["id"])
        titles.append(point.payload["newspaper_title"])
    return titles

def search_semantic(user_query: str, top_k: int = 5, fetch_k: int = 50) -> list[str]:
    embeddings = GoogleGenerativeAIEmbeddings(
    google_api_key="",
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
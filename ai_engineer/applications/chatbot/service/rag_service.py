from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import QdrantClient

from ai_engineer.shared.llm.create_llm import create_gemini_embedding


class DocumentSearchService:
    def __init__(self, qdrant_client: QdrantClient, api_key: str, model_name: str):
        self.qdrant_client = qdrant_client
        self.embedding: GoogleGenerativeAIEmbeddings = create_gemini_embedding(api_key, model_name, output_dimensionality=768)

    def embed_query(self, query: str) -> list[float]:
        return self.embedding.embed_query(query)

    def simlar_searcch_with_vector(
            self,
            vector: list[float],
            collection_name: str,
            fetch_k: int = 5,
            top_k: int = 5,
            with_payload: bool = True,
            with_vectors: bool = False,
        ) -> list[str]:
        search_result = self.qdrant_client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=fetch_k,
            with_payload=with_payload,
            with_vectors=with_vectors
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

    def similar_search_with_query(
        self,
        query: str,
        collection_name: str,
        fetch_k: int = 5,
        top_k: int = 5,
        with_payload: bool = True,
        with_vectors: bool = False,
    ) -> list[str]:
        vector = self.embed_query(query)
        return self.simlar_searcch_with_vector(
            vector=vector,
            collection_name=collection_name,
            fetch_k=fetch_k,
            top_k=top_k,
            with_payload=with_payload,
            with_vectors=with_vectors,
        )

    def retrieve_database_with_document_ids(self, document_ids: list[str]) -> list[str]:
        document_ids = [str(x) for x in document_ids]

        points = self.qdrant_client.retrieve(
            collection_name="newspaper",
            ids=document_ids,
            with_payload=True,
            with_vectors=False,
        )

        output_documents = []


        for point in points:
            output_documents.append({
                "title": point.payload["newspaper_title"],
                "content": point.payload["newspaper_content"],
            })
        
        return output_documents

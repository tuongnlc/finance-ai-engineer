from typing import Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import QdrantClient, models
from ai_engineer.shared.llm.create_llm import create_gemini_embedding
from fastembed import SparseTextEmbedding
from underthesea import word_tokenize
from fastembed import SparseTextEmbedding


class DocumentSearchService:
    def __init__(self, 
            qdrant_client: QdrantClient, 
            collection_name: str, 
            dense_api_key: Optional[str] = None,
            dense_model_name: Optional[str] = None,
            dense_vector_name: Optional[str] = None,
            sparse_model_name: Optional[str] = None,
            sparse_vector_name: Optional[str] = None,
        ):
        self.qdrant_client = qdrant_client
        self.collection_name = collection_name
        if dense_model_name is not None:
            self.dense_embedding: GoogleGenerativeAIEmbeddings = create_gemini_embedding(dense_api_key, dense_model_name, output_dimensionality=768)
            self.dense_vector_name = dense_vector_name
        if sparse_vector_name is not None:
            self.sparse_embedding: SparseTextEmbedding = SparseTextEmbedding(model_name="Qdrant/bm25",  disable_stemmer=True)
            self.sparse_vector_name = sparse_vector_name
        

    def embed_dense_query(self, query: str) -> list[float]:
        return self.dense_embedding.embed_query(query)

    def embed_sparse_query(self, query: str) -> list[float]:
        tokens = word_tokenize(query, format="text")
        sparse_vector = next(self.sparse_embedding.embed([tokens]))
        return sparse_vector

    def simlar_search_with_dense_vector(
            self,
            query: str,
            limit: int = 20,
            with_payload: bool = True,
            with_vectors: bool = False,
            score_threshold: int = 0,
        ) -> list[str]:
        vector = self.embed_dense_query(query)
        search_result = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=limit,
            using=self.dense_vector_name,
            with_payload=with_payload,
            with_vectors=with_vectors,
            score_threshold=score_threshold,
        )
        return search_result.points

    def simlar_search_with_sparse_vector(
            self,
            query: str,
            limit: int = 20,
            with_payload: bool = True,
            with_vectors: bool = False,
            score_threshold: int = 0,
        ) -> list[str]:
        sparse_vector = self.embed_sparse_query(query)
        search_result = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            using=self.sparse_vector_name,
            query=models.SparseVector(
                indices=sparse_vector.indices,
                values=sparse_vector.values
            ),
            limit=limit,
            with_payload=with_payload,
            with_vectors=with_vectors,
            score_threshold=score_threshold,
        )
        return search_result.points

    def similar_search_with_hydrid_search(
        self,
        query: str,
        limit: int = 20,
        with_payload: bool = True,
        with_vectors: bool = False,
        sparse_score_threshold: int = 14,
        dense_score_threshold: int = 0.55,
    ):
        sparse_vector = self.embed_sparse_query(query)
        dense_vector = self.embed_dense_query(query)
        search_results = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            prefetch=[
                models.Prefetch(
                    query=models.SparseVector(
                        indices=sparse_vector.indices,
                        values=sparse_vector.values
                ),
                using=self.sparse_vector_name,
                limit=20,
                score_threshold=sparse_score_threshold,
                prefetch=[
                    models.Prefetch(
                        query=dense_vector,
                        using=self.dense_vector_name,
                        limit=20,
                        score_threshold=dense_score_threshold,
                    )
                ]
                )
            ],
            query=models.FusionQuery(
                fusion=models.Fusion.RRF
            ),
            limit=limit,
            with_payload=with_payload,
            with_vectors=with_vectors,
            # score_threshold=0.3
        )
        return search_results.points

    def retrieve_database_with_document_ids(self,
        points, 
        top_k: int = 5,
    ):
        document_ids = []
        seen = set()

        for point in points:
            doc_id = (point.payload or {}).get("document_id")
            if doc_id is None:
                continue

            doc_id = str(doc_id)
            if doc_id in seen:
                continue

            seen.add(doc_id)
            document_ids.append(doc_id)

            if len(document_ids) >= top_k: #get 5 points
                break

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

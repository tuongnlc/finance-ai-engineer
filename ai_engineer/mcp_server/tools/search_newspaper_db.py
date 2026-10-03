import asyncio
from typing import Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import QdrantClient, models
from ai_engineer.shared.llm.create_llm import create_gemini_embedding
from fastembed import SparseTextEmbedding
from underthesea import word_tokenize
from fastembed import SparseTextEmbedding
from ai_engineer.helpers.build_payload_filter import build_payload_filter


class SearchNewsPaperDB:
    """
        Receive input from query_understand endpoint. 

        Then do search with information
        + query: optimized_search_query # Update query to do multiple search with optimized_search_query
        + filter: main_topic and stock_id
    """
    def __init__(self, 
            # qdrant_client: QdrantClient, 
            collection_name: str, 
            dense_api_key: Optional[str] = None,
            dense_model_name: Optional[str] = None,
            dense_vector_name: Optional[str] = None,
            sparse_model_name: Optional[str] = None,
            sparse_vector_name: Optional[str] = None,
            query_filter: Optional[dict] = None,
        ):
        self.qdrant_client = QdrantClient(url="http://localhost:6333", timeout=600)
        self.collection_name = collection_name
        if dense_model_name is not None:
            self.dense_embedding: GoogleGenerativeAIEmbeddings = create_gemini_embedding(dense_api_key, dense_model_name, output_dimensionality=768)
            self.dense_vector_name = dense_vector_name
        if sparse_vector_name is not None:
            self.sparse_embedding: SparseTextEmbedding = SparseTextEmbedding(model_name="Qdrant/bm25",  disable_stemmer=True)
            self.sparse_vector_name = sparse_vector_name
        self.query_filter = query_filter
        
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
        """
            Search with dense vector. The process is:
            1. Embed query to dense vector.
            2. Query points with dense vector.
            3. Return search result
        """
        vector = self.embed_dense_query(query)
        if self.query_filter is not None:
            query_filter = build_payload_filter(self.query_filter)
        search_result = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=limit,
            using=self.dense_vector_name,
            with_payload=with_payload,
            with_vectors=with_vectors,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )
        return search_result

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
        return search_result

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
        return search_results

    async def retrieve_database_with_user_query(
        self,
        query: str,
        limit: int = 5,
        top_k: int = 5,
        search_type: str = "hybrid",
):
        search_results = await asyncio.to_thread(
            self.similar_search_with_hydrid_search if search_type == "hybrid"
            else self.simlar_search_with_dense_vector if search_type == "dense"
            else self.simlar_search_with_sparse_vector,
            query,
            limit,
        )

        document_ids_for_newspaper = []
        seen = set()

        for point in search_results.points:
            payload = point.payload or {}
            doc_id = payload.get("document_id")
            
            doc_id = str(doc_id)
            if doc_id in seen:
                continue
            seen.add(doc_id)
            if len(document_ids_for_newspaper) < top_k:
                document_ids_for_newspaper.append(doc_id)

        documents = self.qdrant_client.retrieve(
            "newspaper",
            document_ids_for_newspaper,
            True,
            False,
        )
        documents = self.order_document_by_publish_date(documents)
        
        output_text = []
        for doc in documents:
            output_text.append({
                "newspaper_title": doc.payload.get("newspaper_title"),
                "publish_date": doc.payload.get("publish_date"),
                "newspaper_content": doc.payload.get("newspaper_content"),
            })

        return output_text

    def order_document_by_publish_date(self, documents):
        documents.sort(key=lambda x: (x.payload or {}).get("publish_date", ""), reverse=True)
        return documents
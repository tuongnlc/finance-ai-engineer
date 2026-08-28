from ai_engineer.applications.topic_tagging.use_case.add_tagging_to_newspaper_embedded import AddTaggingToNewspaperEmbeddedUseCase
from ai_engineer.applications.topic_tagging.use_case.topic_tagging import TopicTaggingUseCase
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from datetime import date
from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader


def main():
    newspaper_extractor = QdrantExtractorWithPayloadFilter(
        qdrant_url="http://localhost:6333",
        collection_name="newspaper",
        payload_filter={
            "is_topic_tagging": 1
        },
        with_vectors=False,
    )

    join_df_id = newspaper_extractor["id"].to_list()
    qdrant_extractor = QdrantExtractorWithPayloadFilter(
        qdrant_url="http://localhost:6333",
        collection_name="newspaper_embedded",
        payload_filter={
            "document_id": join_df_id
        },
        with_vectors=["bm25_sparse", "gemini_dense_vector"],
    )

    qdrant_loader = QdrantLoader(
        qdrant_url="localhost:6333",
        destination_collection_name="backup_newspaper_embeddded",
    )

    use_case = AddTaggingToNewspaperEmbeddedUseCase(
        newspaper_extractor=newspaper_extractor,
        newspaper_embedded_extractor=qdrant_extractor,
        loader=qdrant_loader
    )
    
    df = use_case.run(
        dense_vector_column="gemini_dense_vector",
        sparse_vector_indices_column="bm25_sparse_indices",
        sparse_vector_values_column="bm25_sparse_values",
    )

if __name__ == "__main__":
    main()

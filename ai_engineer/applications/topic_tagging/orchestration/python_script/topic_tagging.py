from ai_engineer.applications.topic_tagging.use_case.topic_tagging import TopicTaggingUseCase
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from datetime import date
from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader


def main():
    newspaper_extractor = QdrantExtractorWithPayloadFilter(
        qdrant_url="http://qdrant:6333", #when run in docker composer
        collection_name="newspaper",
        payload_filter={
            "is_topic_tagging": 0
        },
        with_vectors=False,
    )

    newspaper_embedded_extractor = QdrantExtractorWithPayloadFilter(
        qdrant_url="http://qdrant:6333", #when run in docker composer
        collection_name="newspaper_embedded",
        payload_filter={},
        with_vectors=["bm25_sparse", "gemini_dense_vector"],
    )

    newspaper_loader = QdrantLoader(
        qdrant_url="http://qdrant:6333", #when run in docker composer
        destination_collection_name="newspaper",
    )

    newspaper_embedded_loader = QdrantLoader(
        qdrant_url="http://qdrant:6333", #when run in docker composer
        destination_collection_name="newspaper_embedded",
    )

    use_case = TopicTaggingUseCase(
        newspaper_extractor=newspaper_extractor,
        newspaper_embedded_extractor=newspaper_embedded_extractor,
        newspaper_loader=newspaper_loader,
        newspaper_embedded_loader=newspaper_embedded_loader,
    )
    df_ = use_case.run()
    # print(df_)
    

if __name__ == "__main__":
    main()

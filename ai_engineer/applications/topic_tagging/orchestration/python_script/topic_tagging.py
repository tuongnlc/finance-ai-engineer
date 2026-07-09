from ai_engineer.applications.topic_tagging.use_case.topic_tagging import TopicTaggingUseCase
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from datetime import date
from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader


def main():
    # df = topic_tagging_use_case.run()
    qdrant_extractor = QdrantExtractorWithPayloadFilter(
    # qdrant_url="localhost:6333",
    qdrant_url="http://qdrant:6333", #when run in docker composer
    collection_name="newspaper",
    payload_filter={
        "is_topic_tagging": 0,
    },
    with_vectors=False,
)

    qdrant_loader = QdrantLoader(
        # qdrant_url="localhost:6333",
        qdrant_url="http://qdrant:6333", #when run in docker composer
        destination_collection_name="newspaper",
    )

    topic_tagging_use_case = TopicTaggingUseCase(
        extractor=qdrant_extractor,
        loader=qdrant_loader,
    )
    df = topic_tagging_use_case.run()

if __name__ == "__main__":
    main()

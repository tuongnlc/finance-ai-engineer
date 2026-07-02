from src.applications.topic_tagging.use_case.topic_tagging import TopicTaggingUseCase
from src.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from datetime import date
from src.shared.data_pipeline.load.qdramt_loader import QdrantLoader



qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url="localhost:6333",
    collection_name="newspaper",
    payload_filter={
        "created_at":"2026-06-25",
        "is_topic_tagging": 0,
    },
    with_vectors=False,
)

qdrant_loader = QdrantLoader(
    qdrant_url="localhost:6333",
    destination_collection_name="newspaper",
)

topic_tagging_use_case = TopicTaggingUseCase(
    extractor=qdrant_extractor,
    loader=qdrant_loader,
)
df = topic_tagging_use_case.run()
# print(df)

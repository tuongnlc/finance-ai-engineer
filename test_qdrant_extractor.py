from src.applications.topic_tagging.use_case.topic_tagging import TopicTaggingUseCase
from src.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from datetime import date
from src.shared.data_pipeline.load.qdramt_loader import QdrantLoader



qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url="localhost:6333",
    collection_name="newspaper",
    payload_filter={
        "publish_date":"2026-05-03",
        "is_topic_tagging": 0,
    },
    with_vectors=False,
)

df_ = qdrant_extractor.extract()
print(len(df_))

df_ = df_.select("publish_date]").min()
print(df_)

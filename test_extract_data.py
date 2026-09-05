from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter


qdrant_extractor = QdrantExtractorWithPayloadFilter(
    # qdrant_url="localhost:6333",
    qdrant_url="http://localhost:6333", #when run in docker composer
    collection_name="newspaper",
    payload_filter={
        "is_topic_tagging": 0,
    },
    with_vectors=False,
)

df = qdrant_extractor.extract()
print(df)
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter

# Test query Qdrant

extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url="localhost:6333",
    collection_name="backup_newspaper_embeddded",
    payload_filter={
        # "is_topic_tagging": 0,
        "publish_date": "2026-07-19",
        "main_topic": ["kinh tế vĩ mô & chính sách", "pháp lý & quản lý nhà nước"],
    },
    with_vectors=False,
)

df_ = extractor.extract()
print(len(df_))
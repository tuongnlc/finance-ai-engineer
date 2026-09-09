

from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter


qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url="http://localhost:6333",
    # qdrant_collection_name="stock_price_embedded",
    collection_name="newspaper",
    payload_filter={"publish_date": "2026-09-07"},
    # with_payload=True,
    with_vectors=True,
)

df_ = qdrant_extractor.extract()
print(len(df_))
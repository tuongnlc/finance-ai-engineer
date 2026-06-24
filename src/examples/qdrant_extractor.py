# /Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/src/shared/data_pipeline/extract/qdrant_extractor.py

from src.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter

test_qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url="http://localhost:6333",
    collection_name="newspaper_embedded",
    payload_filter={},
    with_vectors=True,
)

test_data = test_qdrant_extractor.extract()
print(type(test_data.get_column("vector"))) #<class 'polars.column.VectorColumn'>




# Step 1: Load qdrant points in newspaper collection
import json

import polars as pl
from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from ai_engineer.helpers.migration.add_column_qdrant import add_column_qdrant


qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url="localhost:6333",
    collection_name="newspaper",
    payload_filter={},
    with_vectors=False,
)

df = qdrant_extractor.extract()


df = df.select(["id", "newspaper_title", "newspaper_url", "publish_date", "newspaper_content", "newspaper_summary", "is_embedded", "created_at"])
print(len(df))
print(df.columns)


qdrant_loader = QdrantLoader(
    qdrant_url="localhost:6333",
    destination_collection_name="newspaper",
)

qdrant_loader.load(df, vector_column=None)

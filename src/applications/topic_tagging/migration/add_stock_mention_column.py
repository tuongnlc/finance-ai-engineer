# Step 1: Load qdrant points in newspaper collection
import json

import polars as pl
from src.shared.data_pipeline.load.qdramt_loader import QdrantLoader
from src.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from src.helpers.migration.add_column_qdrant import add_column_qdrant

# Step 1: qdrant extractor
qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url="localhost:6333",
    collection_name="newspaper",
    payload_filter={},
    with_vectors=False,
)

# Step 3: Write transformed data to qdrant collection
qdrant_loader = QdrantLoader(
    qdrant_url="localhost:6333",
    destination_collection_name="newspaper",
)

add_column_qdrant(
    qdrant_loader=qdrant_loader,
    qdrant_extractor=qdrant_extractor,
    column="stock_mention",
    value=[],
    dtype=pl.List(pl.Utf8),
)
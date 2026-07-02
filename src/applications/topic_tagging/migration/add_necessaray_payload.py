# Step 1: Load qdrant points in newspaper collection
import json

import polars as pl
from src.shared.data_pipeline.load.qdramt_loader import QdrantLoader
from src.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from src.helpers.migration.add_column_qdrant import add_column_qdrant


qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url="localhost:6333",
    collection_name="newspaper",
    payload_filter={},
    with_vectors=False,
)

qdrant_loader = QdrantLoader(
    qdrant_url="localhost:6333",
    destination_collection_name="newspaper",
)

# Add stock mention payload if not exists
add_column_qdrant(
    qdrant_loader=qdrant_loader,
    qdrant_extractor=qdrant_extractor,
    column="stock_mention",
    value=[],
    dtype=pl.List(pl.Utf8),
)

# # Add topic_keywords payload if not exists
add_column_qdrant(
    qdrant_loader=qdrant_loader,
    qdrant_extractor=qdrant_extractor,
    column="topic_keywords",
    value=[],
    dtype=pl.List(pl.Utf8),
)

# Add sentiment_analysis payload if not exists
add_column_qdrant(
    qdrant_loader=qdrant_loader,
    qdrant_extractor=qdrant_extractor,
    column="sentiment_analysis",
    value="",
    dtype=pl.Utf8,
)

# Add mention_people payload if not exists
add_column_qdrant(
    qdrant_loader=qdrant_loader,
    qdrant_extractor=qdrant_extractor,
    column="mention_people",
    value=[],
    dtype=pl.List(pl.Utf8),
)

# Add mention stock_funds payload if not exists
add_column_qdrant(
    qdrant_loader=qdrant_loader,
    qdrant_extractor=qdrant_extractor,
    column="mention_stock_funds",
    value=[],
    dtype=pl.List(pl.Utf8),
)

# Add foreign_securities_funds payload if not exists
add_column_qdrant(
    qdrant_loader=qdrant_loader,
    qdrant_extractor=qdrant_extractor,
    column="foreign_securities_funds",
    value=[],
    dtype=pl.List(pl.Utf8),
)

# Add government_policies payload if not exists
add_column_qdrant(
    qdrant_loader=qdrant_loader,
    qdrant_extractor=qdrant_extractor,
    column="government_policies",
    value=[],
    dtype=pl.List(pl.Utf8),
)

# Add is_topic_tagging
add_column_qdrant(
    qdrant_loader=qdrant_loader,
    qdrant_extractor=qdrant_extractor,
    column="is_topic_tagging",
    value=0,
    dtype=pl.Int8,
)

add_column_qdrant(
    qdrant_loader=qdrant_loader,
    qdrant_extractor=qdrant_extractor,
    column="topic_tagging",
    value="",
    dtype=pl.Utf8,
)
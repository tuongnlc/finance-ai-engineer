# Step 1: Load qdrant points in newspaper collection
import json

import polars as pl
from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from ai_engineer.helpers.migration.add_column_qdrant import add_column_qdrant


qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url='http://localhost:6333',
    collection_name='newspaper_embedded',
    payload_filter={
    },
    with_vectors=["bm25_sparse", "gemini_dense_vector"]
)

df_newspaper_embedding = qdrant_extractor.extract()

df_newspaper = df_newspaper_embedding.with_columns(
    pl.col("bm25_sparse").map_elements(lambda v: v.indices if v is not None else [], return_dtype=pl.List(pl.Int32)).alias("bm25_sparse_indices"),
    pl.col("bm25_sparse").map_elements(lambda v: v.values if v is not None else [], return_dtype=pl.List(pl.Float64)).alias("bm25_sparse_values"),
).drop("bm25_sparse")
print(df_newspaper.head())

qdrant_loader = QdrantLoader(
    qdrant_url="localhost:6333",
    destination_collection_name="newspaper_embedded",
)

# Add main_topic payload if not exists
add_column_qdrant(
    qdrant_loader=qdrant_loader,
    qdrant_extractor=qdrant_extractor,
    column="main_topic",
    value=[],
    dtype=pl.List(pl.Utf8),
    dense_vector_column="gemini_dense_vector",
    sparse_vector_indices_column="bm25_sparse_indices",
    sparse_vector_values_column="bm25_sparse_values",
    with_sparse_vector=True,
)

# # # Add stocks_mention payload if not exists
add_column_qdrant(
    qdrant_loader=qdrant_loader,
    qdrant_extractor=qdrant_extractor,
    column="stocks_mention",
    value=[],
    dtype=pl.List(pl.Utf8),
    with_sparse_vector=True,
    sparse_vector_indices_column="bm25_sparse_indices",
    sparse_vector_values_column="bm25_sparse_values",
    dense_vector_column="gemini_dense_vector",
)

# # # Add mention_people payload if not exists
add_column_qdrant(
    qdrant_loader=qdrant_loader,
    qdrant_extractor=qdrant_extractor,
    column="person_mention",
    value=[],
    dtype=pl.List(pl.Utf8),
    with_sparse_vector=True,
    sparse_vector_indices_column="bm25_sparse_indices",
    sparse_vector_values_column="bm25_sparse_values",
    dense_vector_column="gemini_dense_vector",
)

# 

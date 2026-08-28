from ai_engineer.applications.topic_tagging.use_case.add_tagging_to_newspaper_embedded import AddTaggingToNewspaperEmbeddedUseCase
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
import numpy as np
import os
import polars as pl

from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader

qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url='http://localhost:6333',
    collection_name='newspaper_embedded',
    payload_filter={
        "publish_date":"2026-06-17"
    },
    with_vectors=["bm25_sparse", "gemini_dense_vector"]
)
df_newspaper = qdrant_extractor.extract()
df_newspaper = df_newspaper.limit(5)

df_newspaper = df_newspaper.with_columns(
    pl.col("bm25_sparse").map_elements(lambda v: v.indices if v is not None else [], return_dtype=pl.List(pl.Int32)).alias("bm25_sparse_indices"),
    pl.col("bm25_sparse").map_elements(lambda v: v.values if v is not None else [], return_dtype=pl.List(pl.Float64)).alias("bm25_sparse_values"),
).drop("bm25_sparse")
print(df_newspaper.head())

# print(len(df_newspaper))

# Define qdrant loader
qdrant_loader = QdrantLoader(
    qdrant_url="localhost:6333",
    destination_collection_name="backup_newspaper_embeddded",
)
qdrant_loader.load(
    df_newspaper,
    dense_vector_column="gemini_dense_vector",
    sparse_vector_indices_column="bm25_sparse_indices",
    sparse_vector_values_column="bm25_sparse_values",
)

# qdrant_loader.load(df_newspaper,
#     vector_column="gemini_dense_vector",

# )



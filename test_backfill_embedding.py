import os

import numpy as np
import polars as pl

from ai_engineer.applications.topic_tagging.use_case.add_tagging_to_newspaper_embedded import AddTaggingToNewspaperEmbeddedUseCase
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import (
    QdrantExtractorWithPayloadFilter,
)
from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader


# Step 1: Extract newspaper data from qdrant
newspaper_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url="http://localhost:6333",
    collection_name="newspaper",
    payload_filter={
        # "is_topic_tagging": 1
        # "id": "11ffd71e0519497fb9e6c7ff56544fce"
    },
    with_vectors=False,
)

# df_newspaper = qdrant_extractor.extract()

# join_df = df_newspaper.select(
#     ["id", "stocks_mention", "main_topic", "person_mention"]
# ).with_columns(
#     pl.col("id").str.replace_all("-", "").alias("id")
# )

# # print(len(join_df))
# print(join_df.columns)
# # join_df_id = join_df["id"].to_list()

# # join_df_id = join_df_id[:10]
# # print(join_df_id)
# print(len(join_df))
# print(join_df.head())


# # Step 2: Extract newspaper_embedding from qdrant
qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url="http://localhost:6333",
    collection_name="newspaper_embedded",
    payload_filter={
        # "publish_date":"2026-06-17"
        # "document_id": join_df_id
        # "document_id": "11ffd71e0519497fb9e6c7ff56544fce"
    },
    with_vectors=["bm25_sparse", "gemini_dense_vector"],
)

# df_newspaper_embedding = qdrant_extractor.extract()
# print(df_newspaper_embedding.columns)

# df_newspaper_embedding = df_newspaper_embedding.select(
#     [
#         "id",
#         "document_id",
#         "publish_date",
#         "chunk_content",
#         "chunk_index",
#         "bm25_sparse",
#         "gemini_dense_vector",
#     ]
# ).with_columns(
#     pl.col("document_id").str.replace_all("-", "").alias("document_id")
# )

# # df_newspaper_embedding = df_newspaper_embedding.limit(5)
# print(df_newspaper_embedding.head())
# print(len(df_newspaper_embedding))


# # Step 3: Join join_df with df_newspaper_embedding
# # join_df = df_newspaper_embedding.join(join_df, on="document_id", how="inner")
# final_df = df_newspaper_embedding.join(
#     join_df,
#     left_on="document_id",
#     right_on="id",
#     how="inner",
# )

# final_df = final_df.with_columns(
#     pl.col("bm25_sparse")
#     .map_elements(
#         lambda v: v.indices if v is not None else [],
#         return_dtype=pl.List(pl.Int32),
#     )
#     .alias("bm25_sparse_indices"),
#     pl.col("bm25_sparse")
#     .map_elements(
#         lambda v: v.values if v is not None else [],
#         return_dtype=pl.List(pl.Float64),
#     )
#     .alias("bm25_sparse_values"),
# ).drop("bm25_sparse")


# # Define loader
qdrant_loader = QdrantLoader(
    qdrant_url="localhost:6333",
    destination_collection_name="backup_newspaper_embeddded",
)
# qdrant_loader.load(
#     final_df,
#     dense_vector_column="gemini_dense_vector",
#     sparse_vector_indices_column="bm25_sparse_indices",
#     sparse_vector_values_column="bm25_sparse_values",
# )

use_case = AddTaggingToNewspaperEmbeddedUseCase(
    newspaper_extractor=newspaper_extractor,
    newspaper_embedded_extractor=qdrant_extractor,
    loader=qdrant_loader
)

df = use_case.run(
    dense_vector_column="gemini_dense_vector",
    sparse_vector_indices_column="bm25_sparse_indices",
    sparse_vector_values_column="bm25_sparse_values",
)
print(len(df))
print(df.columns)

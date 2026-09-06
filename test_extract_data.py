import uuid
from ai_engineer.applications.topic_tagging.use_case.topic_tagging import TopicTaggingUseCase
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
# ReplaceCharInColumn
from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader
from ai_engineer.shared.data_pipeline.transform.columns import ReplaceCharInColumn, SelectColumns
import polars as pl

# TopicTaggingUseCase

# Step 1: Extract newspaper data from Qdrant collection
qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url='http://localhost:6333',
    collection_name='newspaper_embedded',
    payload_filter={
        # "publish_date": "2026-07-19"
    },
    with_vectors=["bm25_sparse", "gemini_dense_vector"]
)

df_ = qdrant_extractor.extract()
# df_ = df_.limit(10)
# print(len(df_))

# df_ = df_['document_id'].to_list()
# print(df_[:5])

# for i in df_:
#     print(i)
#     print("")
#     print(str(uuid.UUID(i)))

df_newspaper = df_.with_columns(
    pl.col("bm25_sparse").map_elements(lambda v: v.indices if v is not None else [], return_dtype=pl.List(pl.Int32)).alias("bm25_sparse_indices"),
    pl.col("bm25_sparse").map_elements(lambda v: v.values if v is not None else [], return_dtype=pl.List(pl.Float64)).alias("bm25_sparse_values"),
).drop("bm25_sparse")

df_newspaper = df_newspaper.with_columns(
    pl.col("document_id").map_elements(lambda x: str(uuid.UUID(x)), return_dtype=pl.Utf8).alias("document_id"),
)



qdrant_loader = QdrantLoader(
    qdrant_url="localhost:6333",
    destination_collection_name="newspaper_embedded",
)

qdrant_loader.load(
    df_newspaper, 
    dense_vector_column="gemini_dense_vector",
    sparse_vector_indices_column="bm25_sparse_indices",
    sparse_vector_values_column="bm25_sparse_values",
    # with_sparse_vector=True,
)

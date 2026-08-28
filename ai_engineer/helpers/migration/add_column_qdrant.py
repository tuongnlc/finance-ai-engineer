from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from ai_engineer.shared.data_pipeline.transform.columns import AddColumn
from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader
import polars as pl
from typing import Any


def add_column_qdrant(
    qdrant_loader: QdrantLoader,
    qdrant_extractor: QdrantExtractorWithPayloadFilter,
    column: str,
    value: Any,
    dtype: pl.DataType | pl.DataTypeClass | None = None,
    with_sparse_vector: bool = False,
    **kwargs
) -> None:
    """
    Add a column to the qdrant collection.

    Pass ``dtype`` when Polars cannot infer the target type correctly,
    for example with blank list columns such as ``[]``.
    """
    original_data = qdrant_extractor.extract()

    if with_sparse_vector:
        original_data = original_data.with_columns(
            pl.col("bm25_sparse").map_elements(lambda v: v.indices if v is not None else [], return_dtype=pl.List(pl.Int32)).alias("bm25_sparse_indices"),
            pl.col("bm25_sparse").map_elements(lambda v: v.values if v is not None else [], return_dtype=pl.List(pl.Float64)).alias("bm25_sparse_values"),
        ).drop("bm25_sparse")

    original_data_schema = original_data.schema
    
    if column in original_data_schema:
        print(f"Column {column} already exists in the collection {qdrant_extractor.collection_name}")
        return

    transformed_data = AddColumn(column=column, value=value, dtype=dtype).transform(original_data)
    qdrant_loader.load(transformed_data, **kwargs)
    print("Column added to qdrant collection")

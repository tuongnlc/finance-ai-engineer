from src.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from src.shared.data_pipeline.transform.columns import AddColumn
from src.shared.data_pipeline.load.qdramt_loader import QdrantLoader
import polars as pl
from typing import Any


def add_column_qdrant(
    qdrant_loader: QdrantLoader,
    qdrant_extractor: QdrantExtractorWithPayloadFilter,
    column: str,
    value: Any,
    dtype: pl.DataType | pl.DataTypeClass | None = None,
) -> None:
    """
    Add a column to the qdrant collection.

    Pass ``dtype`` when Polars cannot infer the target type correctly,
    for example with blank list columns such as ``[]``.
    """
    original_data = qdrant_extractor.extract()

    original_data_schema = original_data.schema
    
    if column in original_data_schema:
        print(f"Column {column} already exists in the collection {qdrant_extractor.collection_name}")
        return

    transformed_data = AddColumn(column=column, value=value, dtype=dtype).transform(original_data)
    qdrant_loader.load(transformed_data, vector_column=None)
    print("Column added to qdrant collection")

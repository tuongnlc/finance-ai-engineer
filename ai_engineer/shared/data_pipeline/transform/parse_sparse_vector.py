import polars as pl
from ai_engineer.shared.data_pipeline.transform.base import TransformStep
from typing import Any


class ParseSparseVector(TransformStep):
    """
        Parse sparse vector column
        :param sparse_vector_column_name: Sparse vector column name to parse
        :return: The dataframe with the parsed sparse vector indices and values columns
    """
    def __init__(self, 
            sparse_vector_column_name: str,
            indices_column_name: str,
            values_column_name: str,
            ):
        self.sparse_vector_column_name = sparse_vector_column_name
        self.indices_column_name = indices_column_name 
        self.values_column_name = values_column_name 

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        df = df.with_columns(
            pl.col(self.sparse_vector_column_name)
                .map_elements(
                    lambda v: v.indices if v is not None else [],
                    return_dtype=pl.List(pl.Int32),
                )
                .alias(self.indices_column_name),
            pl.col(self.sparse_vector_column_name)
                .map_elements(
                    lambda v: v.values if v is not None else [],
                    return_dtype=pl.List(pl.Float64),
                )
                .alias(self.values_column_name),
        ).drop(self.sparse_vector_column_name)
        return df

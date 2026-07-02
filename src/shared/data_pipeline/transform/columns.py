import polars as pl
from src.shared.data_pipeline.transform.base import TransformStep
from typing import Any



class SelectColumns(TransformStep):
    def __init__(self, columns: list[str]):
        self.columns = columns

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        df= df.select(pl.col(c) for c in self.columns)
        return df


class AddColumn(TransformStep):
    def __init__(
        self,
        column: str,
        value: Any,
        dtype: pl.DataType | pl.DataTypeClass | None = None,
    ):
        self.column = column
        self.value = value
        self.dtype = dtype

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        column_expr = pl.lit(self.value)

        if self.dtype is not None:
            column_expr = column_expr.cast(self.dtype)

        df = df.with_columns(column_expr.alias(self.column))
        return df


class DropColumns(TransformStep):
    def __init__(self, columns: list[str]):
        self.columns = columns

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        df = df.drop(self.columns)
        return df

import polars as pl
from ai_engineer.shared.data_pipeline.transform.base import TransformStep
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
        existing_cols = [c for c in self.columns if c in df.columns]
        if existing_cols:
            df = df.drop(existing_cols)
        return df


class ReplaceCharInColumn(TransformStep):
    def __init__(self, column: str, old_char: str, new_char: str):
        self.column = column
        self.old_char = old_char
        self.new_char = new_char

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        df = df.with_columns(
            pl.col(self.column).str.replace_all(self.old_char, self.new_char).alias(self.column)
        )
        return df
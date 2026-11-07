import re
from typing import Any

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DataType

from ai_engineer.shared.data_pipeline.transform.base import TransformStep


class SelectColumns(TransformStep):
    def __init__(self, columns: list[str]):
        self.columns = columns

    def transform(self, df: DataFrame) -> DataFrame:
        df = df.select(*self.columns)
        return df


class AddColumn(TransformStep):
    def __init__(
        self,
        column: str,
        value: Any,
        dtype: DataType | None = None,
    ):
        self.column = column
        self.value = value
        self.dtype = dtype

    def transform(self, df: DataFrame) -> DataFrame:
        column_expr = F.lit(self.value)

        if self.dtype is not None:
            column_expr = column_expr.cast(self.dtype)

        df = df.withColumn(self.column, column_expr)
        return df


class DropColumns(TransformStep):
    def __init__(self, columns: list[str]):
        self.columns = columns

    def transform(self, df: DataFrame) -> DataFrame:
        existing_cols = [c for c in self.columns if c in df.columns]
        if existing_cols:
            df = df.drop(*existing_cols)
        return df


class ReplaceCharInColumn(TransformStep):
    def __init__(self, column: str, old_char: str, new_char: str):
        self.column = column
        self.old_char = old_char
        self.new_char = new_char

    def transform(self, df: DataFrame) -> DataFrame:
        df = df.withColumn(
            self.column,
            F.regexp_replace(
                F.col(self.column),
                re.escape(self.old_char),
                self.new_char,
            ),
        )
        return df

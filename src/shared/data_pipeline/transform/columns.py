import polars as pl
from src.shared.data_pipeline.transform.base import TransformStep
from typing import Any



class SelectColumns(TransformStep):
    def __init__(self, columns: list[str]):
        self.columns = columns

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        df= df.select(pl.col(c) for c in self.columns)
        return df
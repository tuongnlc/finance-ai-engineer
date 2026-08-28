import polars as pl
from ai_engineer.shared.data_pipeline.transform.base import TransformStep
from typing import Any


class JoinDataFrame(TransformStep):
    """
        Join two dataframe
        :param left_on: The column name to join on the left dataframe
        :param right_on: The column name to join on the right dataframe
        :param how: The type of join to perform
        :return: The joined dataframe
    """
    def __init__(self, left_on: str, right_on: str, how: str = "inner"):
        self.left_on = left_on
        self.right_on = right_on
        self.how = how

    def transform(self, df_left: pl.DataFrame, df_right: pl.DataFrame) -> pl.DataFrame:
        df = df_left.join(
                df_right, 
                left_on=self.left_on,
                right_on=self.right_on,
                how=self.how
        )
        return df

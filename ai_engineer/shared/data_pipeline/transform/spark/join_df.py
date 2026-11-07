from pyspark.sql import DataFrame

from ai_engineer.shared.data_pipeline.transform.base import TransformStep


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

    def transform(self, df_left: DataFrame, df_right: DataFrame) -> DataFrame:
        # Khi 2 bên join cùng tên cột thì dùng join theo tên cột, Spark sẽ gộp thành
        # 1 cột duy nhất (tránh trùng cột -> lỗi ambiguous khi select về sau).
        on = (
            self.left_on
            if self.left_on == self.right_on
            else df_left[self.left_on] == df_right[self.right_on]
        )
        df = df_left.join(
            df_right,
            on=on,
            how=self.how,
        )
        return df

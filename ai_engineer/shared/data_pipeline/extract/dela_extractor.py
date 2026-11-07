from pyspark.sql import SparkSession
from .base import BaseExtractor



class DeltaExtractor(BaseExtractor):
    def __init__(
        self,
        table_uri: str,
        spark: SparkSession,
    ):
        self.table_uri = table_uri
        self.spark = spark

    def extract(self):
        """
            Extract data from parquet file
        """
        return self.spark.read.table(self.table_uri)

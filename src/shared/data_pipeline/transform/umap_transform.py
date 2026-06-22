from src.shared.data_pipeline.transform.base import TransformStep
import polars as pl
import numpy as np
from umap import UMAP
import mlflow
import tempfile



class UmapTransform(TransformStep):
    def __init__(self, 
            n_components: int, 
            min_dist: float, 
            metric: str, 
            random_state: int
        ):
        self.n_components = n_components
        self.min_dist = min_dist
        self.metric = metric
        self.random_state = random_state

    def _convert_df_to_array(self, df: pl.DataFrame, embedding_column_name: str) -> np.ndarray:
        """
            Convert the input DataFrame to a numpy array.
        """
        embedding_column = df.get_column(embedding_column_name)
        return np.vstack(embedding_column.to_numpy())

    def transform(self, df: pl.DataFrame, embedding_column_name: str) -> pl.DataFrame:
        """
            Load model from MLFlow and do transform for the input DataFrame.
        """
        embedding_array = self._convert_df_to_array(df, embedding_column_name)

        MODEL_URI = "models:/umap_model@prod"
        mlflow.set_tracking_uri("http://localhost:5000")

        with tempfile.TemporaryDirectory() as tmpdir:
            model = mlflow.sklearn.load_model(MODEL_URI, dst_path=tmpdir)
            reduced_embeddings = model.transform(embedding_array)

        reduced_embedding_series = pl.Series(
            name=f"{embedding_column_name}_umap", 
            values=reduced_embeddings.tolist() # Chuyển numpy array sang list of lists
        )
        output_df = df.with_columns(reduced_embedding_series)
        return output_df

    def log_to_mlfow(self) -> None:
        """
            Log the UMAP reduction parameters to MLFlow.
        """
        pass

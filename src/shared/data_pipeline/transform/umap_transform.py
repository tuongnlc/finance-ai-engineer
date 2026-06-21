from src.shared.data_pipeline.transform.base import TransformStep
import polars as pl
import numpy as np
from umap import UMAP

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
            Apply UMAP reduction to the input DataFrame.
        """
        embedding_array = self._convert_df_to_array(df, embedding_column_name)

        umap_transform = UMAP(
            n_components=self.n_components,
            min_dist=self.min_dist,
            metric=self.metric,
            random_state=self.random_state,
        )

        reduced_embeddings = umap_transform.fit_transform(embedding_array)

        reduced_embedding_series = pl.Series(
            name=f"{embedding_column_name}_umap", 
            values=reduced_embeddings.tolist() # Chuyển numpy array sang list of lists
        )

        output_df = df.with_columns(reduced_embedding_series)
        print(output_df)
        
        return output_df

    def log_to_mlfow(self) -> None:
        """
            Log the UMAP reduction parameters to MLFlow.
        """
        pass

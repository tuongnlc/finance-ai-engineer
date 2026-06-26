import os

from umap import UMAP
import mlflow
import tempfile
import time
import polars as pl
import numpy as np

MODEL_URI = "models:/umap_model@prod"


class InferenceUmap:
    def _configure_mlflow_http_timeout(self) -> None:
        """
            Configure MLflow request timeout.
        """
        os.environ["MLFLOW_HTTP_REQUEST_TIMEOUT"] = os.getenv(
            "MLFLOW_HTTP_REQUEST_TIMEOUT", "10"
        )

    def _load_model(self) -> UMAP:
        """
            Load the UMAP model from MLFlow.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            model = mlflow.sklearn.load_model(MODEL_URI, dst_path=tmpdir)
            return model

    def _preprocess(self, df_: pl.DataFrame, embedding_column: str) -> np.ndarray:
        """
            Convert the input DataFrame to numpy array.
        """
        vectors = df_.get_column(embedding_column)
        embedding_vectors = np.vstack(vectors.to_numpy())
        return embedding_vectors

    def predict(
        self,
        df_: pl.DataFrame,
        embedding_column: str = "vector",
        output_column: str = "vector_umap",
    ) -> pl.DataFrame:
        """
            Transform embeddings using a UMAP model loaded from MLflow.
        """
        
        self._configure_mlflow_http_timeout()
        # mlflow.set_tracking_uri("http://localhost:5000")
        mlflow.set_tracking_uri("http://mlflow-server:5000") #When run in docker
        
        mlflow.set_experiment("umap_model_inference")
        with mlflow.start_run():
            model = self._load_model()
            embedding_vectors = self._preprocess(df_, embedding_column=embedding_column)
            start_time = time.time()
            reduced_embeddings = model.transform(embedding_vectors)
            
            latency = (time.time() - start_time) * 1000

            output_len = len(reduced_embeddings)
            output_shape = reduced_embeddings.shape

            log_payload = {
                "latency": latency,
                "output_len": output_len,
                "output_rows": output_shape[0],
                "output_dims": output_shape[1],
            }
            mlflow.log_metrics(log_payload)

            reduced_embedding_series = pl.Series(
                name=output_column,
                values=reduced_embeddings.tolist(),
            )
            output_df = df_.with_columns(reduced_embedding_series)
            return output_df

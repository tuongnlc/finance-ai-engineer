import os

from umap import UMAP
import mlflow
import numpy as np
from mlflow import MlflowClient


class TrainingUmap:
    def __init__(self, 
                 n_components: int = 5,
                 min_dist: float = 0.1,
                 metric: str = "cosine",
                 random_state: int = 42):
        self.n_components = n_components
        self.min_dist = min_dist
        self.metric = metric
        self.random_state = random_state

    def _configure_mlflow_http_timeout(self) -> None:
        """
            Configure MLflow request timeout.
        """
        os.environ["MLFLOW_HTTP_REQUEST_TIMEOUT"] = os.getenv(
            "MLFLOW_HTTP_REQUEST_TIMEOUT", "10"
        )

    def _build_model(self) -> UMAP:
        """
            Build the UMAP model.
        """
        return UMAP(
            n_components=self.n_components,
            min_dist=self.min_dist,
            metric=self.metric,
            random_state=self.random_state
        )

    def _log_artifacts(self, 
            mlflow_client: mlflow.MlflowClient,
            model: UMAP, 
            model_name: str = "umap_model", 
            model_alias: str = "prod",
            ) :
        """
            Log the UMAP model to MLFlow.
        """
        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            name=model_name,
            registered_model_name=model_name,
            serialization_format="cloudpickle",
        )

        versions = mlflow_client.search_model_versions(f"name='{model_name}'")
        latest_version = max(int(v.version) for v in versions)

        mlflow_client.set_registered_model_alias(
            name=model_name,
            alias=model_alias,
            version=str(latest_version),
        )
        return model_info

    def _log_params(self) -> None:
        """
            Log the UMAP model parameters to MLFlow.
        """
        mlflow.log_param("n_components", self.n_components)
        mlflow.log_param("min_dist", self.min_dist)
        mlflow.log_param("metric", self.metric)
        mlflow.log_param("random_state", self.random_state)

    def train(self, X_train: np.ndarray) -> None:
        """
            Train the UMAP model on the input DataFrame.
        """
        self._configure_mlflow_http_timeout()
        # mlflow.set_tracking_uri("http://localhost:5000")
        mlflow.set_tracking_uri("http://mlflow-server:5000") #When run in docker
        
        mlflow.set_experiment("umap_model_training")
        with mlflow.start_run():
            # mlflow_client = MlflowClient(tracking_uri="http://localhost:5000")
            mlflow_client = MlflowClient(tracking_uri="http://mlflow-server:5000")
            self._log_params()
            model = self._build_model()
            reduced_embeddings = model.fit_transform(X_train)
            model_info = self._log_artifacts(
                mlflow_client=mlflow_client,
                model=model
            )
            return model_info, reduced_embeddings

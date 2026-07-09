

from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
import numpy as np
import os

# Step 1: Extract data from qdrant
qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url='http://localhost:6333',
    collection_name='newspaper_topic_modelling_embedded',
    payload_filter={
        "publish_date":"2026-06-17"
    },
    with_vectors=True
)

test_data = qdrant_extractor.extract()
print(test_data)

# Step 2: Apply HDBSCAN
from hdbscan import HDBSCAN

reduced_embeddings = test_data.get_column("vector")
reduced_embeddings = np.vstack(reduced_embeddings.to_numpy())

hdbscan_model = HDBSCAN(
    min_cluster_size=10, metric="euclidean", cluster_selection_method="eom",prediction_data=True
).fit(reduced_embeddings)

clusters = hdbscan_model.labels_
print(clusters)

# Load to mlflow
import mlflow
from mlflow import MlflowClient

os.environ["MLFLOW_HTTP_REQUEST_TIMEOUT"] = os.getenv("MLFLOW_HTTP_REQUEST_TIMEOUT", "30")
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_registry_uri("http://localhost:5000")
mlflow.set_experiment("hdbscan_model_training")

with mlflow.start_run():
    mlflow_client = MlflowClient(tracking_uri="http://localhost:5000")
    mlflow.log_param("min_cluster_size", 10)
    mlflow.log_param("metric", "euclidean")
    mlflow.log_param("cluster_selection_method", "eom")
    mlflow.log_param("prediction_data", True)
    mlflow.log_metric("n_samples", int(len(clusters)))
    mlflow.log_metric("n_noise", int((clusters == -1).sum()))
    mlflow.log_metric("n_clusters", int(len(set(clusters)) - (1 if -1 in set(clusters) else 0)))

    model_name = "hdbscan_model"
    model_info = mlflow.sklearn.log_model(
        sk_model=hdbscan_model,
        name=model_name,
        registered_model_name=model_name,
        serialization_format="cloudpickle",
    )

    versions = mlflow_client.search_model_versions(f"name='{model_name}'")
    latest_version = max(int(v.version) for v in versions)
    mlflow_client.set_registered_model_alias(
        name=model_name,
        alias="prod",
        version=str(latest_version),
    )

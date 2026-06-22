from qdrant_extractor import QdrantExtractorWithPayloadFilter
import polars as pl
import numpy as np
import mlflow
import joblib
import os



#query embedding_newspaper
qrant_extractor_embedding_newspaper = QdrantExtractorWithPayloadFilter(
    qdrant_url="http://localhost:6333",
    collection_name="newspaper_embedded",
    payload_filter={"publish_date": "2026-06-17"},
    with_vectors=True,
)


data_embedding_newspaper = qrant_extractor_embedding_newspaper.extract(  
).get_column("vector")
print(type(data_embedding_newspaper))
#<class 'polars.column.VectorColumn'>
X = np.vstack(data_embedding_newspaper.to_numpy())
# print(X.shape) #(10, 768)

from umap import UMAP
import time

import mlflow
from mlflow import MlflowClient

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("test_mlflow_artifact_v3")

REGISTERED_MODEL_NAME = "umap_model"
MODEL_ALIAS = "prod"

with mlflow.start_run(run_name="umap_reduction") as run:
    mlflow.log_param("n_components", 5)
    mlflow.log_param("min_dist", 0.0)
    mlflow.log_param("metric", "cosine")
    mlflow.log_param("random_state", 42)

    umap_model = UMAP(
        n_components=5,
        min_dist=0.0,
        metric="cosine",
        random_state=42,
    )

    reduced_embeddings = umap_model.fit_transform(X)

    model_info = mlflow.sklearn.log_model(
        sk_model=umap_model,
        name="umap_model",
        registered_model_name=REGISTERED_MODEL_NAME,
        serialization_format="cloudpickle",
    )

client = MlflowClient(tracking_uri="http://localhost:5000")

versions = client.search_model_versions(f"name='{REGISTERED_MODEL_NAME}'")
latest_version = max(int(v.version) for v in versions)

client.set_registered_model_alias(
    name=REGISTERED_MODEL_NAME,
    alias=MODEL_ALIAS,
    version=str(latest_version),
)

print(f"Model URI co dinh de infer: models:/{REGISTERED_MODEL_NAME}@{MODEL_ALIAS}")
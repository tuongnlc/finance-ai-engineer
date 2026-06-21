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

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("test_mlflow_artifact_v3") 

with mlflow.start_run(run_name="umap_reduction") as run:
    mlflow.log_param("n_components", 5)
    mlflow.log_param("min_dist", 0.0)
    mlflow.log_param("metric", "cosine")
    mlflow.log_param("random_state", 42)

    start_time = time.time()

    umap_model = UMAP(
        n_components=5, 
        min_dist=0.0, 
        metric='cosine', 
        random_state=42
    )

    reduced_embeddings = umap_model.fit_transform(X)
    print(reduced_embeddings.shape) #(10, 5)
    print(f"UMAP reduction time: {time.time() - start_time}")
    duration = time.time() - start_time
    
    # Log metrics
    mlflow.log_metric("umap_reduction_time_sec", duration)

    mlflow.sklearn.log_model(
        sk_model=umap_model,
        name="umap_model",
        serialization_format="cloudpickle",
    )


    print(f"Đã log xong! Xem trên MLflow với Run ID: {run.info.run_id}")

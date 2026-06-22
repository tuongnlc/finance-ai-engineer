from qdrant_extractor import QdrantExtractorWithPayloadFilter
import numpy as np
import mlflow
import tempfile

qrant_extractor_embedding_newspaper = QdrantExtractorWithPayloadFilter(
    qdrant_url="http://localhost:6333",
    collection_name="newspaper_embedded",
    payload_filter={"publish_date": "2026-06-17"},
    with_vectors=True,
)

data_embedding_newspaper = qrant_extractor_embedding_newspaper.extract().get_column("vector")
print(type(data_embedding_newspaper))
X = np.vstack(data_embedding_newspaper.to_numpy())

MODEL_URI = "models:/umap_model@prod"

mlflow.set_tracking_uri("http://localhost:5000")

with tempfile.TemporaryDirectory() as tmpdir:
    model = mlflow.sklearn.load_model(MODEL_URI, dst_path=tmpdir)
    reduced = model.transform(X)
    print(reduced.shape)
    print(reduced)
from src.applications.topic_modeling.training.training_umap import TrainingUmap
import numpy as np
from src.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter

training_umap = TrainingUmap()

qrant_extractor_embedding_newspaper = QdrantExtractorWithPayloadFilter(
    qdrant_url="http://localhost:6333",
    collection_name="newspaper_embedded",
    payload_filter={"publish_date": "2026-06-17"},
    with_vectors=True,
)


data_embedding_newspaper = qrant_extractor_embedding_newspaper.extract(  
).get_column("vector")
print(type(data_embedding_newspaper))

test_data = np.vstack(data_embedding_newspaper.to_numpy())

test_training = training_umap.train(test_data)
print(test_training)
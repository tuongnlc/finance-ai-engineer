from qdrant_extractor import QdrantExtractorWithPayloadFilter
import polars as pl
import numpy as np



#query embedding_newspaper
qrant_extractor_embedding_newspaper = QdrantExtractorWithPayloadFilter(
    qdrant_url="http://localhost:6333",
    collection_name="newspaper_embedded",
    payload_filter={"publish_date": "2026-06-17"},
    with_vectors=True,
)

# data_embedding_newspaper = qrant_extractor_embedding_newspaper.extract(  
# ).get_column("vector").to_list()
# print(data_embedding_newspaper)
# print(len(data_embedding_newspaper))

data_embedding_newspaper = qrant_extractor_embedding_newspaper.extract(  
).get_column("vector")
X = np.vstack(data_embedding_newspaper.to_numpy())
print(X.shape) #(10, 768)

from umap import UMAP
import time

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
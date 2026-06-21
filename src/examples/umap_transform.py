# /Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/src/shared/data_pipeline/extract/qdrant_extractor.py

from src.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter

test_qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url="http://localhost:6333",
    collection_name="newspaper_embedded",
    payload_filter={"publish_date": "2026-06-17"},
    with_vectors=True,
)

test_data = test_qdrant_extractor.extract()

# Apply UMAP reduction
from src.shared.data_pipeline.transform.umap_transform import UmapTransform

import time

start_time = time.time()

umap_transform = UmapTransform(n_components=2, min_dist=0.1, metric="cosine", random_state=42)
test_data = umap_transform.transform(test_data, "vector")
print(test_data)
print(f"UMAP reduction time: {time.time() - start_time}")

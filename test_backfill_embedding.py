
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
import numpy as np
import os

# Step 1: Extract newspaperdata from qdrant
qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url='http://localhost:6333',
    collection_name='newspaper',
    payload_filter={
        # "publish_date":"2026-06-17"
    },
    with_vectors=True
)

df_newspaper = qdrant_extractor.extract()

print(len(df_newspaper))

# Step 2: Extract newspaper_embedding from qdrant
qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url='http://localhost:6333',
    collection_name='newspaper_embedded',
    payload_filter={
        # "publish_date":"2026-06-17"
    },
    with_vectors=True
)

df_newspaper_embedding = qdrant_extractor.extract()

print(len(df_newspaper_embedding))

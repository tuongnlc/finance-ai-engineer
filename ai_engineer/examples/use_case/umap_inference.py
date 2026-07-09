# /Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/shared/data_pipeline/extract/qdrant_extractor.py

from ai_engineer.applications.topic_modeling.use_case.umap_inference import InferenceUMAPUseCase
from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from ai_engineer.applications.topic_modeling.inference.inference_umap import InferenceUmap
from ai_engineer.shared.data_pipeline.transform.columns import SelectColumns
from datetime import date

inference_umap_use_case = InferenceUMAPUseCase(
    publish_date=date(2026, 6, 17),
)

inference_umap_use_case.load(
    
)

# /Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/src/shared/data_pipeline/extract/qdrant_extractor.py

from src.applications.topic_modeling.use_case.umap_inference import InferenceUMAPUseCase
from src.shared.data_pipeline.load.qdramt_loader import QdrantLoader
from src.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from src.applications.topic_modeling.inference.inference_umap import InferenceUmap
from src.shared.data_pipeline.transform.columns import SelectColumns
from datetime import date

inference_umap_use_case = InferenceUMAPUseCase(
    publish_date=date(2026, 6, 17),
)

inference_umap_use_case.load(
    
)

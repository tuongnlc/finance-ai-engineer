# /Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/src/shared/data_pipeline/extract/qdrant_extractor.py

from src.applications.topic_modeling.use_case.umap_inference import InferenceUMAPUseCase
from datetime import date


def main(publish_date: str | date):
    """
        Main function to run UMAP inference.

        Receive publish_date from airflow.
    """
    if isinstance(publish_date, str):
        publish_date = date.fromisoformat(publish_date)
    inference_umap_use_case = InferenceUMAPUseCase(
    # publish_date=date(2026, 6, 17),
    publish_date=publish_date,
)
    inference_umap_use_case.load()


if __name__ == "__main__":
    main()

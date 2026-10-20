from json import load
import random
import time
import uuid
from dotenv import load_dotenv
import os

from ai_engineer.applications.topic_summary.application.call_llm import CallLLMWithStructuredOutput
from ai_engineer.applications.topic_summary.application.pdf_generator import PdfSummarizationGenerator
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader
import polars as pl
from qdrant_client import QdrantClient, models

load_dotenv()

list_of_api_keys = [
    "GCP_PROJECT_1",
    "GCP_PROJECT_2",
    "GCP_PROJECT_3",
    "GCP_PROJECT_4",
    "GCP_PROJECT_5",
    "GCP_PROJECT_6",
    "GCP_PROJECT_7",
    "GCP_PROJECT_8",
]

api_key = random.choice(list_of_api_keys)

topic_tagging_api_key = os.getenv(api_key)
topic_tagging_model = os.getenv("TOPIC_TAGGING_MODEL")
BATCH_SIZE = 15
BATCH_SLEEP_SECONDS = 60


class TopicSummaryUseCase:
    def __init__(
            self,
            extractor: QdrantExtractorWithPayloadFilter,
            llm_caller: CallLLMWithStructuredOutput,
            loader: QdrantLoader,
        ):
        self.extractor = extractor
        self.llm_caller = llm_caller
        self.loader = loader

    def extract(self):
        df = self.extractor.extract()
        return df

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        # return df
        inputs = df.to_dicts()
        responses = self.llm_caller.call_llm_in_batch(
                inputs=inputs,
            )
        rows = []
        for item in responses:
            for news_type, summary in item["response"].root.items():
                rows.append({
                    "id": uuid.uuid4(),
                    "document_id": item["document_id"],
                    "publish_date": item["publish_date"],
                    "stocks_mention": item["stocks_mention"],
                    "person_mention": item["person_mention"],
                    "news_type": news_type,
                    "news_summary": summary.summary,
                    "sentiment_analysis": summary.sentiment_analysis,
                    "circular_and_policy": getattr(summary, "circular_and_policy", []),
                    "legal_documents_and_regulations": getattr(summary, "legal_documents_and_regulations", []),
                    "fund_name": getattr(summary, "fund_name", []),
                })
        df = pl.DataFrame(rows)
        return df

    def _close_clients(self):
        if hasattr(self.extractor, "close"):
            self.extractor.close()

    def run(self, loading_date: str):
        try:
            # Step 1: Delete before load
            self.loader.delete_before_load(loading_date)
            
            # Step 2: Extract data
            df = self.extract()
            
            # Step 3: Transform data
            df = self.transform(df)
            
            # Step 4: Load to qdrant
            self.loader.load(df)

        finally:
            self._close_clients()
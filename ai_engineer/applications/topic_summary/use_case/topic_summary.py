import random
import time
from dotenv import load_dotenv
import os

from ai_engineer.applications.topic_summary.application.call_llm import CallLLMWithStructuredOutput
from ai_engineer.applications.topic_summary.application.pdf_generator import PdfSummarizationGenerator
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter

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
            pdf_generator: PdfSummarizationGenerator,
        ):
        self.extractor = extractor
        self.llm_caller = llm_caller
        self.pdf_generator = pdf_generator

    def extract(self):
        df = self.extractor.extract()
        return df

    def _close_clients(self):
        if hasattr(self.extractor, "close"):
            self.extractor.close()

    def run(self):
        try:
            df = self.extract()

            inputs = df.to_dicts()

            #call_llm for summarization task
            responses = self.llm_caller.call_llm_in_batch(
                inputs=inputs,
            )
            print(responses)
            #combine inputs and responses
            output_list_call_llm = []

            # Add if else logic to handle type of output format:
            if self.pdf_generator.report_type == "Báo cáo thông tin doanh nghiệp":
                for row, response in zip(inputs, responses):
                    content_dict = {
                        "stocks_mention": row["stocks_mention"],
                        "person_mention": row["person_mention"],
                    }
                    content_dict.update(response.model_dump())
                    output_list_call_llm.append(content_dict)
            elif self.pdf_generator.report_type == "Báo cáo thông tin kinh tế vĩ mô & chính sách":
                for row, response in zip(inputs, responses):
                    content_dict = {
                        "stocks_mention": "",
                        "person_mention": row.get("person_mention", ""),
                    }
                    content_dict.update(response.model_dump())
                    output_list_call_llm.append(content_dict)
            # print(output_list_call_llm)
            
            # # Generate pdf from output_list_call_llm
            self.pdf_generator.run(
                content=output_list_call_llm
            )
            
            # return output_list_call_llm
        finally:
            self._close_clients()
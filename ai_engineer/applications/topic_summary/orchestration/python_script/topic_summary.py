import random
from pathlib import Path
from datetime import date
from ai_engineer.applications.topic_summary.application.call_llm import CallLLMWithStructuredOutput
from ai_engineer.applications.topic_summary.application.models import TopicAnalysisOutput
from ai_engineer.applications.topic_summary.application.pdf_generator import PdfSummarizationGenerator
from ai_engineer.applications.topic_summary.use_case.topic_summary import TopicSummaryUseCase
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from dotenv import load_dotenv
import os
from ai_engineer.shared.llm.create_llm import create_gemini_llm

load_dotenv()
# publish_date = "2026-08-29"
publish_date = date.today().strftime("%Y-%m-%d")
report_type = "Báo cáo thông tin doanh nghiệp"
print(f"Export data for {publish_date} for {report_type}")

#Create extractor
extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url="http://qdrant:6333",
    collection_name="newspaper",
    payload_filter={
        "publish_date": publish_date,
        "main_topic": "quản trị doanh nghiệp"
    }
)

#Create llm caller
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
GCP_API_KEY = random.choice(list_of_api_keys)

llm_api_key = os.getenv(GCP_API_KEY)

llm = create_gemini_llm(
    api_key=llm_api_key,
    model_name="gemini-3.5-flash-lite",
    temperature=0,
)

llm_caller = CallLLMWithStructuredOutput(
    llm=llm,
    prompt_name="topic_summary__business",
    llm_api_key=llm_api_key,
    structure_output=TopicAnalysisOutput,
)

#Create pdf generator
_orchestration_dir = Path(__file__).resolve().parent.parent
font_path = str(_orchestration_dir / "resources" / "Arial Unicode.ttf")

_output_dir = _orchestration_dir / "resources" / "pdf_generator"
# _output_dir.mkdir(parents=True, exist_ok=True)
output_pdf_path = str(_output_dir / f"bao_cao_doanh_nghiep_{publish_date}.pdf")

pdf_generator = PdfSummarizationGenerator(
    font_path=font_path,
    report_date=publish_date,
    report_type=report_type,
    output_pdf_path=output_pdf_path,
)

# Using in use case
use_case = TopicSummaryUseCase(
    extractor=extractor,
    llm_caller=llm_caller,
    pdf_generator=pdf_generator,
)

def main():
    use_case.run()



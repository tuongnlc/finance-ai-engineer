from ai_engineer.applications.topic_summary.application.call_llm import CallLLMWithStructuredOutput
from ai_engineer.applications.topic_summary.application.models import TopicAnalysisOutput
from ai_engineer.applications.topic_summary.application.pdf_generator import PdfSummarizationGenerator
from ai_engineer.applications.topic_summary.use_case.topic_summary import TopicSummaryUseCase
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from dotenv import load_dotenv
import os
from ai_engineer.shared.llm.create_llm import create_gemini_llm

load_dotenv()
publish_date = "2026-08-28"

#Create extractor
extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url="http://localhost:6333",
    collection_name="newspaper",
    payload_filter={
        "publish_date": publish_date,
        "main_topic": "quản trị doanh nghiệp"
    }
)

#Create llm caller
llm_api_key = os.getenv("GCP_PROJECT_7")

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
font_path = "/Library/Fonts/Arial Unicode.ttf"
pdf_generator = PdfSummarizationGenerator(
    font_path=font_path,
    report_date=publish_date,
    report_type="Báo cáo thông tin doanh nghiệp",
)

# Using in use case
use_case = TopicSummaryUseCase(
    extractor=extractor,
    llm_caller=llm_caller,
    pdf_generator=pdf_generator,
)

df = use_case.run()
print(df)


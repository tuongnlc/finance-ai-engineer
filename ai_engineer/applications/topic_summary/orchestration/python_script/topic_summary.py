import random
from pathlib import Path
from ai_engineer.applications.topic_summary.application.call_llm import CallLLMWithStructuredOutput
from ai_engineer.applications.topic_summary.application.models import (
    TopicAnalysisOutput,
    MacroNewspaperSummaryOutput,
)
from ai_engineer.applications.topic_summary.application.pdf_generator import PdfSummarizationGenerator
from ai_engineer.applications.topic_summary.use_case.topic_summary import TopicSummaryUseCase
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from dotenv import load_dotenv
import os
from ai_engineer.shared.llm.create_llm import create_gemini_llm

load_dotenv()

GCP_API_KEY_NAMES = [
    "GCP_PROJECT_1",
    "GCP_PROJECT_2",
    "GCP_PROJECT_3",
    "GCP_PROJECT_4",
    "GCP_PROJECT_5",
    "GCP_PROJECT_6",
    "GCP_PROJECT_7",
    "GCP_PROJECT_8",
]

_TOPIC_CONFIG = {
    "business": {
        "report_type": "Báo cáo thông tin doanh nghiệp",
        "main_topic": "quản trị doanh nghiệp",
        "prompt_name": "topic_summary__business",
        "structure_output": TopicAnalysisOutput,
        "pdf_filename": "bao_cao_doanh_nghiep_{publish_date}.pdf",
    },
    "macro": {
        "report_type": "Báo cáo kinh tế vĩ mô & chính sách",
        "main_topic": "kinh tế vĩ mô & chính sách",
        "prompt_name": "topic_summary__macro",
        "structure_output": MacroNewspaperSummaryOutput,
        "pdf_filename": "bao_cao_kinh_te_vi_mo_{publish_date}.pdf",
    },
}


def build_use_case(publish_date: str, topic_type: str, llm_api_key: str) -> TopicSummaryUseCase:
    if topic_type not in _TOPIC_CONFIG:
        raise ValueError(f"topic_type must be one of {list(_TOPIC_CONFIG.keys())}")

    cfg = _TOPIC_CONFIG[topic_type]
    report_type = cfg["report_type"]
    print(f"Export data for {publish_date} for {report_type}")

    extractor = QdrantExtractorWithPayloadFilter(
        qdrant_url="http://qdrant:6333",
        collection_name="newspaper",
        payload_filter={
            "publish_date": publish_date,
            "main_topic": cfg["main_topic"],
        },
    )

    llm = create_gemini_llm(
        api_key=llm_api_key,
        model_name="gemini-3.5-flash-lite",
        temperature=0,
    )

    llm_caller = CallLLMWithStructuredOutput(
        llm=llm,
        prompt_name=cfg["prompt_name"],
        llm_api_key=llm_api_key,
        structure_output=cfg["structure_output"],
    )

    _orchestration_dir = Path(__file__).resolve().parent.parent
    font_path = str(_orchestration_dir / "resources" / "Arial Unicode.ttf")

    _output_dir = _orchestration_dir / "resources" / "pdf_generator"
    output_pdf_path = str(_output_dir / cfg["pdf_filename"].format(publish_date=publish_date))

    pdf_generator = PdfSummarizationGenerator(
        font_path=font_path,
        report_date=publish_date,
        report_type=report_type,
        output_pdf_path=output_pdf_path,
    )

    return TopicSummaryUseCase(
        extractor=extractor,
        llm_caller=llm_caller,
        pdf_generator=pdf_generator,
    )


def main(publish_date: str, topic_type: str, llm_api_key: str):
    use_case = build_use_case(publish_date, topic_type, llm_api_key)
    use_case.run()

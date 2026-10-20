import random
from pathlib import Path
import time
from ai_engineer.applications.topic_summary.application.call_llm import CallLLMWithStructuredOutput
from ai_engineer.applications.topic_summary.application.models import (
    BusinessNewspaperSummaryOutput,
    MacroNewspaperSummaryOutput,
    MarketNewspaperSummaryOutput,
    FundNewspaperSummaryOutput,
    LawNewspaperSummaryOutput,
)
from ai_engineer.applications.topic_summary.application.pdf_generator import PdfSummarizationGenerator
from ai_engineer.applications.topic_summary.use_case.topic_summary import TopicSummaryUseCase
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from dotenv import load_dotenv
import os
from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader
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
    "business": { # Quản trị Doanh nghiệp & Tài chính Doanh nghiệp
        "report_type": "Báo cáo thông tin doanh nghiệp",
        "main_topic": "quản trị doanh nghiệp",
        "prompt_name": "topic_summary__business",
        "structure_output": BusinessNewspaperSummaryOutput,
    },
    "macro": { # Kinh tế vĩ mô & chính sách
        "report_type": "Báo cáo kinh tế vĩ mô & chính sách",
        "main_topic": "kinh tế vĩ mô & chính sách",
        "prompt_name": "topic_summary__macro",
        "structure_output": MacroNewspaperSummaryOutput,
    },
    "market": { # Thị trường & giao dịch
        "report_type": "Báo cáo thị trường & giao dịch",
        "main_topic": "thị trường & giao dịch",
        "prompt_name": "topic_summary__market",
        "structure_output": MarketNewspaperSummaryOutput,
    },
    "fund": { # Quỹ & Danh mục đầu tư
        "report_type": "Báo cáo quỹ & danh mục đầu tư",
        "main_topic": "quỹ & danh mục đầu tư",
        "prompt_name": "topic_summary__fund",
        "structure_output": FundNewspaperSummaryOutput,
    },
    "law": { # Pháp lý & quản lý nhà nước
        "report_type": "Báo cáo pháp lý & quản lý nhà nước",
        "main_topic": "pháp lý & quản lý nhà nước",
        "prompt_name": "topic_summary__law",
        "structure_output": LawNewspaperSummaryOutput,
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

    loader = QdrantLoader(
        qdrant_url="http://qdrant:6333",
        destination_collection_name="newspaper_summary",
    )

    return TopicSummaryUseCase(
        extractor=extractor,
        llm_caller=llm_caller,
        loader=loader,
    )


def main(publish_date: str, topic_type: str, llm_api_key: str):
    use_case = build_use_case(publish_date, topic_type, llm_api_key)
    use_case.run(publish_date)
    time.sleep(60)

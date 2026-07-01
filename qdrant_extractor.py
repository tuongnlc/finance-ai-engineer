import json

import polars as pl
from src.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts.chat import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Step 1: qdrant extractor
qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url="localhost:6333",
    collection_name="newspaper",
    payload_filter={
        "created_at":"2026-06-25"
    },
    with_vectors=False,
)

data_ = qdrant_extractor.extract()
data_ = data_.limit(5)

print(data_)
## Create article column
def build_article(x: dict):
    return json.dumps(
        {
            "title": x["newspaper_title"],
            "description": x["newspaper_summary"],
            "content": x["newspaper_content"],
        },
        ensure_ascii=False,
    )


data_ = data_.with_columns(
    pl.struct(["newspaper_title", "newspaper_summary", "newspaper_content"])
    .map_elements(build_article, return_dtype=pl.Utf8)
    .alias("article")
)

# print(data_.head())


# Step 2: topic tagging
from typing import List, Literal
from pydantic import BaseModel

class StockDetail(BaseModel):
    name: str
    summary: str
    writers_attitude: Literal["Positive", "Negative", "Neutral"]


class NewspaperSummary(BaseModel):
    topic_keywords: List[str]
    overall_sentiment: Literal["Positive", "Negative"]
    stocks: List[str]
    stocks_details: List[StockDetail]
    people: List[str]
    stock_funds: List[str]
    foreign_securities_funds: List[str]
    government_policies: List[str]

parser = PydanticOutputParser(pydantic_object=NewspaperSummary)

newspaper_summary_template = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "[PERSONA] You are a financial expert. Your expertise spans stock analysis, account management, and financial analysis (including monetary policy and public investment).\n"
            "[TASK] Read and understand newspapers, then extract information related to the stock market, market trends, and any stock-related details (company names, related people, etc.).\n"
            "[CONTEXT] You operate within a bank like Techcombank or Viettinbank. Think and respond like a financial expert.\n"
            "[FORMAT] Structure your answer as follows:\n"
            "1. What topic does this newspaper talk about? Return main keywords.\n"
            "2. Overall, is this news negative or positive? Return 'Positive' or 'Negative'.\n"
            "3. What stocks are mentioned? If yes return Name of the stocks seperated by ', '. If no, return 'None'.\n"
            "3.1. For each stock: summary and the writer's attitude.\n"
            "4. Who is mentioned? If yes return Name of the people seperated by ', '. If no, return 'None'.\n"
            "5. What stock funds are mentioned?\n"
            ". Any foreign securities funds are mentioned? If yes, return name of the foreign securities funds.\n If no, return 'None'.\n"
            ". What stock funds are mentioned? If yes return Name of the stock funds seperated by ', '. If no, return 'None'.\n"
            "6. Any new government policy mentioned? If yes, return Name of the policy policy seperated by ', '\n If no, return 'None'.\n"
            "\n"
            "Return ONLY valid JSON (no markdown, no extra text) with this schema:\n"
            "{{\n"
            '  "topic_keywords": ["..."],\n'
            '  "overall_sentiment": "Positive" | "Negative",\n'
            '  "stocks": ["..."],\n'
            '  "stocks_details": [{{"name": "...", "summary": "...", "writers_attitude": "Positive" | "Negative" | "Neutral"}}],\n'
            '  "people": ["..."],\n'
            '  "stock_funds": ["..."],\n'
            '  "foreign_securities_funds": ["..."],\n'
            '  "government_policies": ["..."]\n'
            "}}\n"
            "\n"
            "{format_instructions}\n"

            "--- START OF EXAMPLE ---\n"
            "[EXAMPLE INPUT]\n"
            "Title: Công ty chứng khoán chỉ ra tác động ít được chú ý của Thông tư 25, ảnh hưởng đến nhóm bất động sản, xây dựng\n"
            "Description: Động thái chính sách này được đưa ra trong bối cảnh thanh khoản của hệ thống ngân hàng...\n"
            "Content: Ngày 22/4/2026, Ngân hàng Nhà nước đã chính thức ban hành Thông tư 25/2026...\n\n"
            
            "[EXAMPLE OUTPUT]\n"
            "{{\n"
            '  "topic_keywords": ["Thông tư 25/2026", "Ngân hàng Nhà nước", "tỷ lệ an toàn vốn", "thanh khoản hệ thống"],\n'
            '  "overall_sentiment": "Positive",\n'
            '  "stocks": ["ACBS"],\n'
            '  "stocks_details": [\n'
            '    {{\n'
            '      "name": "ACBS",\n'
            '      "summary": "Khối phân tích đưa ra nhận định chuyên môn về tác động của Thông tư 25/2026 đến hệ thống ngân hàng và chi phí vốn.",\n'
            '      "writers_attitude": "Neutral"\n'
            "    }}\n"
            "  ],\n"
            '  "people": [],\n'
            '  "stock_funds": ["Dragon Capital"],\n'
            '  "foreign_securities_funds": [],\n'
            '  "government_policies": ["Thông tư 25/2026/TT-NHNN sửa đổi Thông tư 22/2019/TT-NHNN"]\n'
            "}}\n"
            "--- END OF EXAMPLE ---"
        ),
        HumanMessagePromptTemplate.from_template(
            "Please summarize the following article:\n\n"
            "Title: {title}\n"
            "Description: {description}\n"
            "Content:\n"
            '"""\n'
            "{content}\n"
            '"""'
        ),
    ]
)

# articles = [json.loads(article) for article in data_.get_column("article").to_list()]
# # print(json.dumps(articles[0], ensure_ascii=False, indent=2))

# llm = ChatGoogleGenerativeAI(
#     model="gemini-3.1-flash-lite",
#     api_key="AQ.Ab8RN6KqOPkfj0oKqSRtXP_zM1aZYZ41-c0SagYVly55BwNZ8Q",
#     temperature=0.3,
#     max_tokens=None,
#     timeout=None,
#     max_retries=0,
# )

# prompt = newspaper_summary_template.partial(format_instructions=parser.get_format_instructions())
# chain = prompt | llm | parser
# results = chain.batch(articles, config={"max_concurrency": 5})

# for idx, result in enumerate(results, start=1):
#     print(f"=== Result {idx} ===")
#     print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))

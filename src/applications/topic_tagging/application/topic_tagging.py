from typing import List
from pydantic import BaseModel, ConfigDict, field_validator
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import json
from models import NewspaperSummary


class TopicTaggingApplication():
    def __init__(self, llm_model: ChatGoogleGenerativeAI):
        self.llm_model = llm_model
        self.parser = PydanticOutputParser(pydantic_object=NewspaperSummary)
        self.prompt = newspaper_summary_template

# parser = PydanticOutputParser(pydantic_object=NewspaperSummary)

newspaper_summary_template = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "[PERSONA] You are a financial expert. Your expertise spans stock analysis, account management, and financial analysis (including monetary policy and public investment).\n"
            "[TASK] Read and understand newspapers, then extract information related to the stock market, market trends, and any stock-related details (company names, related people, etc.).\n"
            "[CONTEXT] You operate within a bank like Techcombank or Viettinbank. Think and respond like a financial expert.\n"
            "[FORMAT] Structure your answer as follows:\n"
            "1. What topic does this newspaper talk about? Return main keywords.\n"
            "2. What stocks are mentioned? Return a JSON list of stock tickers/names. If none, return [].\n"
            "3. Who is mentioned? Return a JSON list of people names. If none, return [].\n"
            "4. Any foreign securities funds are mentioned? Return a JSON list of fund names. If none, return [].\n"
            "5. What stock funds are mentioned? Return a JSON list of fund names. If none, return [].\n"
            "6. Any new government policy mentioned? Return a JSON list of policy names. If none, return [].\n"
            "\n"
            "Return ONLY valid JSON (no markdown, no extra text) with this schema. id is the id of the article this value is keep the same between the input and output.\n"
            "{{\n"
            '  "id": "...",\n'
            '  "topic_keywords": ["..."],\n'
            '  "stock_mention": ["..."],\n'
            '  "mention_people": ["..."],\n'
            '  "mention_stock_funds": ["..."],\n'
            '  "foreign_securities_funds": ["..."],\n'
            '  "government_policies": ["..."]\n'
            "}}\n"
            "\n"
            "{format_instructions}\n"

            "--- START OF EXAMPLE ---\n"
            "[EXAMPLE INPUT]\n"
            '"id": "03308960-a935-4b80-a05f-9bfb450e393d"'
            '"Title": "Công ty chứng khoán chỉ ra tác động ít được chú ý của Thông tư 25, ảnh hưởng đến nhóm bất động sản, xây dựng\n"'
            '"Description": "Động thái chính sách này được đưa ra trong bối cảnh thanh khoản của hệ thống ngân hàng...\n"'
            '"Content": "Ngày 22/4/2026, Ngân hàng Nhà nước đã chính thức ban hành Thông tư 25/2026...\n\n"'
            
            "[EXAMPLE OUTPUT]\n"
            "{{\n"
            '  "id": "03308960-a935-4b80-a05f-9bfb450e393d",\n'
            '  "topic_keywords": ["Thông tư 25/2026", "Ngân hàng Nhà nước", "tỷ lệ an toàn vốn", "thanh khoản hệ thống"],\n'
            '  "stock_mention": ["ACBS"],\n'
            '  "mention_people": [],\n'
            '  "mention_stock_funds": ["Dragon Capital"],\n'
            '  "foreign_securities_funds": [],\n'
            '  "government_policies": ["Thông tư 25/2026/TT-NHNN sửa đổi Thông tư 22/2019/TT-NHNN"]\n'
            "}}\n"
            "--- END OF EXAMPLE ---"
        ),
        HumanMessagePromptTemplate.from_template(
            "Please summarize the following article:\n\n"
            "id: {id}\n"
            "Title: {title}\n"
            "Description: {description}\n"
            "Content:\n"
            '"""\n'
            "{content}\n"
            '"""'
        ),
    ]
)

articles = [json.loads(article) for article in data_.get_column("article").to_list()]
# print(json.dumps(articles[0], ensure_ascii=False, indent=2))


llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    api_key="",
    temperature=0.3,
    max_tokens=None,
    timeout=None,
    max_retries=0,
)

import time
start_time = time.time()

prompt = newspaper_summary_template.partial(format_instructions=parser.get_format_instructions())
chain = prompt | llm | parser
results = chain.batch(articles, config={"max_concurrency": 5})

llm_output = []
for idx, result in enumerate(results, start=1):
    print(f"=== Result {idx} ===")
    print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
    llm_output.append(result.model_dump())
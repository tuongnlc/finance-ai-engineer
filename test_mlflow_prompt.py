import json
import os
import mlflow
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

from ai_engineer.shared.llm.create_llm import create_gemini_llm

load_dotenv()

llm = create_gemini_llm(
    api_key=os.getenv("LLM_CHAT_API_KEY_1"),
    model_name="gemini-3.1-flash-lite",
    temperature=0,
)


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part["text"] for part in content
            if isinstance(part, dict) and "text" in part
        )
    return str(content)


@mlflow.trace
def run_prompt():
    prompt = mlflow.genai.load_prompt("prompts:/finance_agent_2026.test_schema.query_understand_prompt/1")
    messages = json.loads(prompt.to_single_brace_format())
    template = ChatPromptTemplate.from_messages(
        [(m["role"], m["content"]) for m in messages]
    )
    chain = template | llm
    response = chain.invoke({
        "question": "What is MLflow?",
        "question_context": "MLflow is a tool for building high-quality agents!",
    })
    return _extract_text(response.content)


print(run_prompt())

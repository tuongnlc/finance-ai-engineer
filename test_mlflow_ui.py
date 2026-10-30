# test_send_trac_to_mlflow
import mlflow

mlflow.langchain.autolog()

from databricks_langchain import ChatDatabricks
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

from dotenv import load_dotenv
from qdrant_client import QdrantClient

# from ai_engineer.helpers.prompt.prompt_registry import prompt_register
load_dotenv()

# from ai_engineer.applications.chatbot.service.rag_service import DocumentSearchService
from ai_engineer.shared.llm.create_llm import create_gemini_embedding, create_gemini_llm
from ai_engineer.helpers.prompt.prompt_registry.prompt_register import PromptRegister
import os



llm_api_key = os.getenv("LLM_CHAT_API_KEY_1")

llm = create_gemini_llm(
    api_key=llm_api_key,
    model_name="gemini-3.1-flash-lite",
    temperature=0,
)


# You can replace 'endpoint' with any Databricks hosted model from here: http://<workspace-url>/ml/endpoints
# llm = ChatDatabricks(endpoint="databricks-meta-llama-3-3-70b-instruct")

llm = create_gemini_llm(
    api_key=llm_api_key,
    model_name="gemini-3.1-flash-lite",
    temperature=0,
)
@tool
def search(query: str):
    """Call to surf the web."""
    if "mlflow" in query.lower():
        return "MLflow is a tool for building high-quality agents!"
    return "I couldn't find any results."
  
tools = [search]
agent_executor = create_react_agent(llm, tools)

agent_executor.invoke( {"messages": [HumanMessage(content="What is MLflow?")]})


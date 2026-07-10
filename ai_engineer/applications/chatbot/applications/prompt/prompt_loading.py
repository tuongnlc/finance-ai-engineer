import os
import mlflow
from langchain_core.prompts import ChatPromptTemplate


class ChatbotPromptLoading:
    def __init__(self):
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000") #use localhost cause frontend fun in local
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_registry_uri(tracking_uri)
        self.prompt_name = "chatbot_prompt" #Cause we use this class for Chatbot Prompt only

    @staticmethod
    def _to_langchain_chat_prompt(template: str | list[dict]) -> ChatPromptTemplate:
        if isinstance(template, str):
            return ChatPromptTemplate.from_messages([("human", template)])

        role_map = {"user": "human", "assistant": "ai", "system": "system", "human": "human", "ai": "ai"}
        return ChatPromptTemplate.from_messages(
            [(role_map.get(m["role"], m["role"]), m["content"]) for m in template]
        )

    @staticmethod
    def _escape_braces_for_langchain(template: list[dict], variables: set[str]) -> list[dict]:
        for m in template:
            c = m["content"]
            for v in variables: c = c.replace(f"{{{v}}}", f"__{v}__")
            c = c.replace("{", "{{").replace("}", "}}")
            for v in variables: c = c.replace(f"__{v}__", f"{{{v}}}")
            m["content"] = c
        return template

    def load_and_parse_prompt(self) -> ChatPromptTemplate:
        prompt = mlflow.genai.load_prompt(self.prompt_name)        
        langchain_template = prompt.to_single_brace_format()
        return self._to_langchain_chat_prompt(langchain_template)

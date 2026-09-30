import os
from langchain_core.prompts import ChatPromptTemplate
import mlflow
from mlflow import MlflowClient



RESERVED_PROMPT_ALIASES = {"latest"}


class PromptRegister:
    def __init__(self):
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_registry_uri(tracking_uri)

    def _prompt_alias_assign(self, prompt_name: str, alias_name: str):
        if alias_name.lower() in RESERVED_PROMPT_ALIASES:
            return
        mlflow_client = MlflowClient()
        versions = mlflow_client.search_prompt_versions(prompt_name)
        latest_version = max(int(v.version) for v in versions)
        mlflow_client.set_prompt_alias(
            name=prompt_name,
            alias=alias_name,
            version=latest_version,
        )
    
    def register_prompt(self, prompt_name, prompt_template, alias_name: str = "production", enable: bool = False):
        if enable:
            mlflow.register_prompt(prompt_name, prompt_template)
            self._prompt_alias_assign(prompt_name, alias_name)
    
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
    
    def load_and_parse_prompt(self, prompt_name: str) -> ChatPromptTemplate:
        prompt = mlflow.genai.load_prompt(prompt_name)        
        langchain_template = prompt.to_single_brace_format()
        return self._to_langchain_chat_prompt(langchain_template)
        

from threading import RLock
from typing import Optional

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

from ai_engineer.shared.llm.create_llm import create_gemini_llm
from ai_engineer.applications.chatbot.applications.io_schemas import LLMResponseOutput
from ai_engineer.applications.chatbot.applications.prompt.prompt_loading import ChatbotPromptLoading


class LLMCallerService:
    _lock = RLock()
    _prompts: dict[tuple[str, str], object] = {}
    _llm_cache: dict[tuple[str, str, float], object] = {}

    def __init__(
        self,
        api_key: str,
        model_name: str,
        temperature: float,
        prompt_name: str,
        add_parser: bool = False,
        pydantic_object: Optional[type[BaseModel]] = None,
    ):
        self._config = (api_key, model_name, temperature)
        self.llm = self._get_llm(api_key, model_name, temperature)
        self.add_parser = add_parser
        self.prompt_name = prompt_name

        if add_parser:
            actual_pydantic = pydantic_object if pydantic_object is not None else LLMResponseOutput
            self._parser: Optional[PydanticOutputParser] = PydanticOutputParser(
                pydantic_object=actual_pydantic
            )
            self._pydantic_key = actual_pydantic.__name__
        else:
            self._parser = None
            self._pydantic_key = "__no_parser__"

    def _get_prompt(self):
        key = (self.prompt_name, self._pydantic_key)
        if key in self.__class__._prompts:
            return self.__class__._prompts[key]

        with self.__class__._lock:
            if key not in self.__class__._prompts:
                template = ChatbotPromptLoading(prompt_name=self.prompt_name).load_and_parse_prompt()
                if self._parser is not None:
                    prompt = template.partial(
                        format_instructions=self._parser.get_format_instructions()
                    )
                else:
                    prompt = template.partial(format_instructions="")
                self.__class__._prompts[key] = prompt
        return self.__class__._prompts[key]

    @classmethod
    def _get_llm(cls, api_key: str, model_name: str, temperature: float):
        key = (api_key, model_name, temperature)
        cached = cls._llm_cache.get(key)
        if cached is not None:
            return cached

        with cls._lock:
            cached = cls._llm_cache.get(key)
            if cached is None:
                cached = create_gemini_llm(api_key, model_name, temperature)
                cls._llm_cache[key] = cached
        return cached

    def _extract_text(self, content: object) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, str):
                    text_parts.append(part)
                elif isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])
            return "".join(text_parts)
        return str(content)

    def call_llm(self, user_question: str, question_context: str = None) -> str:
        prompt = self._get_prompt()
        llm = self.llm

        if self.add_parser:
            chain = prompt | llm | self._parser
        else:
            chain = prompt | llm

        try:
            response = chain.invoke(
                {
                    "question": user_question,
                    "question_context": question_context,
                }
            )
            content = response.content if hasattr(response, "content") else response
            return self._extract_text(content)
        except Exception as e:
            if self.add_parser:
                fallback_chain = prompt | llm
                response = fallback_chain.invoke(
                    {
                        "question": user_question,
                        "question_context": question_context,
                    }
                )
                return self._extract_text(response.content)
            raise e

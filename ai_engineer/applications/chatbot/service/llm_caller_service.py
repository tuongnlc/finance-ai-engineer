from threading import RLock

from langchain_core.output_parsers import PydanticOutputParser

from ai_engineer.shared.llm.create_llm import create_gemini_llm
from ai_engineer.applications.chatbot.applications.models import LLMResponse
from ai_engineer.applications.chatbot.applications.prompt.prompt_loading import ChatbotPromptLoading

class LLMCallerService:
    _lock = RLock()
    _template = None
    _prompt = None
    _parser = PydanticOutputParser(pydantic_object=LLMResponse)
    _llm_cache: dict[tuple[str, str, float], object] = {}

    def __init__(
        self,
        api_key: str,
        model_name: str,
        temperature: float,
    ):
        self._config = (api_key, model_name, temperature)
        self.llm = self._get_llm(api_key, model_name, temperature)

    @classmethod
    def _get_template(cls):
        if cls._template is not None:
            return cls._template

        with cls._lock:
            if cls._template is None:
                cls._template = ChatbotPromptLoading().load_and_parse_prompt()
        return cls._template

    @classmethod
    def _get_prompt(cls):
        if cls._prompt is not None:
            return cls._prompt

        with cls._lock:
            if cls._prompt is None:
                cls._template = ChatbotPromptLoading().load_and_parse_prompt()
                cls._prompt = cls._template.partial(
                    format_instructions=cls._parser.get_format_instructions()
                )
        return cls._prompt

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

    def call_llm(self, user_question: str, question_context: str = None) -> str:
        prompt = self._get_prompt()
        llm = self.llm

        chain = prompt | llm | self._parser

        response = chain.invoke(
            {
                "question": user_question,
                "question_context": question_context,
            }
        )
        return response.content

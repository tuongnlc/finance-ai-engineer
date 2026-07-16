from threading import RLock

from langchain_core.output_parsers import PydanticOutputParser

from ai_engineer.shared.llm.create_llm import create_gemini_llm
from ai_engineer.applications.chatbot.applications.models import LLMResponse
from ai_engineer.applications.chatbot.applications.prompt.prompt_loading import ChatbotPromptLoading


class LLMCallerService:
    _lock = RLock()
    _prompts: dict[str, object] = {}
    _parser = PydanticOutputParser(pydantic_object=LLMResponse)
    _llm_cache: dict[tuple[str, str, float], object] = {}

    def __init__(
        self,
        api_key: str,
        model_name: str,
        temperature: float,
        prompt_name: str,
        add_parser: bool = False,
    ):
        self._config = (api_key, model_name, temperature)
        self.llm = self._get_llm(api_key, model_name, temperature)
        self.add_parser = add_parser
        self.prompt_name = prompt_name

    @classmethod
    def _get_prompt(cls, prompt_name: str):
        if prompt_name in cls._prompts:
            return cls._prompts[prompt_name]

        with cls._lock:
            if prompt_name not in cls._prompts:
                template = ChatbotPromptLoading(prompt_name=prompt_name).load_and_parse_prompt()
                prompt = template.partial(
                    format_instructions=cls._parser.get_format_instructions()
                )
                cls._prompts[prompt_name] = prompt
        return cls._prompts[prompt_name]

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
        prompt = self._get_prompt(self.prompt_name)
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
            # If add_parser is True, response is an LLMResponse object
            # If add_parser is False, response is an AIMessage object
            content = response.content if hasattr(response, "content") else response
            return self._extract_text(content)
        except Exception as e:
            # Fallback for parsing errors or other issues
            if self.add_parser:
                # If parser fails, try to get raw output from LLM
                fallback_chain = prompt | llm
                response = fallback_chain.invoke(
                    {
                        "question": user_question,
                        "question_context": question_context,
                    }
                )
                return self._extract_text(response.content)
            raise e

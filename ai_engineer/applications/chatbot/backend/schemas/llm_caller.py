from datetime import date
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from uuid import UUID


class LLMCallerRequest(BaseModel):
    id: UUID
    content: str
    question_context: Optional[str] = None


class LLMCallerResponse(BaseModel):
    id: UUID
    response: str


class LLMCallerWithoutContextRequest(BaseModel):
    content: str


class ToolCallingRequest(BaseModel):
    """
        Tool calling request for stock chatbot.

        Args:
            original_query: The original query of the request.
            vietnamese_with_diacritics: The Vietnamese sentence of the request with diacritics.
            question_type: The type of the question.
            main_topic: The main topic of the question.
            stock_id: The stock ID of the question.
            target_year: The target year of the question.
            document_type: The type of the document.
            optimized_search_query: The optimized search query of the question.
        Returns:
            The response of the request.
       """
    id: UUID
    original_query: str
    vietnamese_with_diacritics: str
    question_type: str
    main_topic: str
    stock_id: str
    target_year: str
    document_type: str
    optimized_search_query: str

class ToolCallingResponse(BaseModel):
    """
        Tool calling response for stock chatbot.
    """
    id: UUID
    tool_output: str
    tool_name: str
    input_message: str
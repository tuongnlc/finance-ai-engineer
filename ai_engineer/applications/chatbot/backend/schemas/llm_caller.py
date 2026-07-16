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
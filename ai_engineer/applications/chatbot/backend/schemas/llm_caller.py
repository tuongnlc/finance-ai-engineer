from datetime import date
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from uuid import UUID


class LLMCallerRequest(BaseModel):
    id: UUID
    content: str


class LLMCallerResponse(BaseModel):
    id: UUID
    response: str
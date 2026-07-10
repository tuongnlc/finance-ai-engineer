from datetime import date
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class LLMResponseRequest(BaseModel):
    id: UUID
    message_id: UUID
    conversation_id: UUID
    llm_response: str
    content_type: str = "text"
    attachments: Optional[list[dict[str, Any]]] = None
    created_at: date = Field(default_factory=date.today)


class LLMResponseResponse(LLMResponseRequest):
    pass

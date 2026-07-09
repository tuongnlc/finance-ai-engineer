from datetime import date
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum



class ConversationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"


class CreateConversationRequest(BaseModel):
    id: UUID
    user_id: Optional[str] = None
    space_id: Optional[str] = None
    created_timestamp: int = None
    content: str
    created_at: date = Field(default_factory=date.today)


class CreateConversationResponse(BaseModel):
    id: UUID
    user_id: Optional[str] = None
    space_id: Optional[str] = None
    created_timestamp: int = None
    status: Optional[ConversationStatus] = None
    created_at: date = Field(default_factory=date.today)

class GetConversationResponse(CreateConversationResponse):
    pass

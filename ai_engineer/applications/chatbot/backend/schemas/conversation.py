from datetime import date
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from uuid import UUID



class ConversationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"


class CreateConversationRequest(BaseModel):
    id: UUID
    session_id: UUID
    title: Optional[str] = None
    user_id: Optional[str] = None
    space_id: Optional[str] = None
    created_timestamp: int
    created_at: date = Field(default_factory=date.today)


class CreateConversationResponse(BaseModel):
    id: UUID
    title: Optional[str] = None

class GetConversationResponse(BaseModel):
    id: UUID
    session_id: UUID
    title: Optional[str] = None
    user_id: Optional[str] = None
    space_id: Optional[str] = None
    created_timestamp: int
    status: ConversationStatus
    created_at: date


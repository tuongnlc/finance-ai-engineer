from datetime import date
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from uuid import UUID



class MessageStatus(str, Enum):
    PENDING = "PENDING"
    FAILED = "FAILED"


class CreateMessageRequest(BaseModel):
    id: UUID
    space_id: Optional[str] = None
    conversation_id: UUID
    user_id: Optional[str] = None
    created_timestamp: int
    content_type: Optional[str] = None
    message_url: Optional[str] = None
    status: Optional[MessageStatus] = None
    content: str
    attachments: Optional[str] = None
    created_at: date = Field(default_factory=date.today)


class CreateMessageResponse(BaseModel):
    id: UUID
    space_id: Optional[str] = None
    conversation_id: UUID
    user_id: Optional[str] = None
    created_timestamp: int
    content_type: Optional[str] = None
    message_url: Optional[str] = None
    status: Optional[MessageStatus] = None
    content: str
    attachments: Optional[str] = None
    created_at: date = Field(default_factory=date.today)


class GetMessageResponse(CreateMessageResponse):
    pass

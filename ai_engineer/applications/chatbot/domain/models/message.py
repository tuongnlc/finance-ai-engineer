

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import uuid
from datetime import date



class MessageStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Message:
    id: uuid.UUID
    conversation_id: uuid.UUID
    created_timestamp: int
    content: str
    space_id: Optional[str] = None
    user_id: Optional[str] = None
    content_type: Optional[str] = None
    message_url: Optional[str] = None
    status: Optional[MessageStatus] = None
    attachments: Optional[str] = None
    created_at: date = field(default_factory=date.today)

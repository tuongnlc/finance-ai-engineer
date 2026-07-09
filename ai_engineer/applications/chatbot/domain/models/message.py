

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
    space_id: Optional[str] = None
    conversation_id: Optional[uuid.UUID]
    user_id: Optional[str] = None
    created_timestamp: int
    content_type: str = None
    message_url: [str] = None
    status: Optional[MessageStatus] = None
    content: str 
    attachment: Optional[str] = None
    created_at: date = field(default_factory=date.today)

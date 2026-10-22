from dataclasses import dataclass, field
import uuid


@dataclass
class Session:
    """
        Domain session model
    """
    id: uuid.UUID
    conversation_id: uuid.UUID
    created_timestamp: int
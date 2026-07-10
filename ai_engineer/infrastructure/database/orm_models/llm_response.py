from ai_engineer.infrastructure.database.models import Base
import uuid
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from sqlalchemy import BigInteger

from sqlalchemy.orm import DeclarativeBase

from ai_engineer.infrastructure.database.orm_models.base import Base



class LLMResponseORM(Base):
    """
        Saving llm response data in chatbot application
    """
    __tablename__ = 'llm_response'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    llm_response: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(255), nullable=False, default="TEXT")
    attachments: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column(
        default=date.today,
        nullable=False,
    )

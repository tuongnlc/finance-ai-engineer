"""
    SQLAlchemy declarative models to do migration for postgresql

"""
import uuid
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from sqlalchemy import BigInteger


class Base(DeclarativeBase):
    pass


class Conversation(Base):
    """
        Saving conversation data in chatbot application
    """
    __tablename__ = 'conversation'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    space_id: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=True)
    created_timestamp: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(255), nullable=False, default="PENDING")
    created_at: Mapped[date] = mapped_column(
        default=date.today(),
        nullable=False,
    )
    

class Message(Base):
    """
        Saving message data in chatbot application
    """
    __tablename__ = 'message'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    space_id: Mapped[str] = mapped_column(String(255), nullable=True)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    user_id: Mapped[str] = mapped_column(String(255), nullable=True)
    created_timestamp: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_url: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(255), nullable=False, default="PENDING")
    content: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column(
        default=date.today,
        nullable=False,
    )


class LLMResponse(Base):
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
    llm_response: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(255), nullable=False, default="TEXT")
    attachments: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column(
        default=date.today,
        nullable=False,
    )
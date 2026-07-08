"""SQLAlchemy declarative models (bảng) dùng cho PostgreSQL."""
import uuid
from sqlalchemy import String
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
    
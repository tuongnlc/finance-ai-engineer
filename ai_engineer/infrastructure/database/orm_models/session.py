import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger
from ai_engineer.infrastructure.database.orm_models.base import Base


class SessionORM(Base):
    __tablename__ = 'session'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    created_timestamp: Mapped[int] = mapped_column(BigInteger, nullable=False)

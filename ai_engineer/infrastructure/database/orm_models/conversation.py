from ai_engineer.infrastructure.database.models import Base
import uuid
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from sqlalchemy import BigInteger


from ai_engineer.infrastructure.database.orm_models.base import Base



class ConversationORM(Base):
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
        default=date.today,
        nullable=False,
    )

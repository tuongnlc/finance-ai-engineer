import uuid
from datetime import date
from sqlalchemy import Date, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from ai_engineer.infrastructure.database.orm_models.base import Base


class NewspaperSummaryORM(Base):
    """
        Saving newspaper summary data in chatbot application
    """
    __tablename__ = 'newspaper_summary'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    publish_date: Mapped[date] = mapped_column(Date, nullable=True, index=True)
    stocks_mention: Mapped[str] = mapped_column(String(255), nullable=True)
    person_mention: Mapped[str] = mapped_column(String(255), nullable=True)
    newspaper_type: Mapped[str] = mapped_column(String(255), nullable=True)
    newspaper_summary: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment_analysis: Mapped[str] = mapped_column(String(255), nullable=True)
    circular_and_policy: Mapped[str] = mapped_column(String(255), nullable=True)
    legal_documents_and_regulations: Mapped[str] = mapped_column(String(255), nullable=True)
    fund_name: Mapped[str] = mapped_column(String(255), nullable=True)
    main_topic: Mapped[str] = mapped_column(String(255), nullable=True)

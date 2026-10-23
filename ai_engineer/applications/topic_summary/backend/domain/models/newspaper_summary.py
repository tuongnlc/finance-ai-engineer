from dataclasses import dataclass
from typing import Optional
import uuid
from datetime import date


@dataclass
class NewspaperSummary:
    id: uuid.UUID
    document_id: uuid.UUID
    newspaper_summary: str
    publish_date: Optional[date] = None
    stocks_mention: Optional[str] = None
    person_mention: Optional[str] = None
    newspaper_type: Optional[str] = None
    sentiment_analysis: Optional[str] = None
    circular_and_policy: Optional[str] = None
    legal_documents_and_regulations: Optional[str] = None
    fund_name: Optional[str] = None
    main_topic: Optional[str] = None
    is_favorite: int = 0

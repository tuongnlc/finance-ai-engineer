"""change newspaper summary columns to text

Revision ID: b3f1a9c72d40
Revises: 5a39c0451ffb
Create Date: 2026-10-23 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3f1a9c72d40'
down_revision: Union[str, Sequence[str], None] = '5a39c0451ffb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Cac cot luu list (nhieu gia tri) nen doi sang Text de khong bi gioi han 255 ky tu
_COLUMNS = [
    "stocks_mention",
    "person_mention",
    "circular_and_policy",
    "legal_documents_and_regulations",
    "fund_name",
]


def upgrade() -> None:
    """Upgrade schema."""
    for column in _COLUMNS:
        op.alter_column(
            'newspaper_summary',
            column,
            existing_type=sa.String(length=255),
            type_=sa.Text(),
            existing_nullable=True,
        )


def downgrade() -> None:
    """Downgrade schema."""
    for column in _COLUMNS:
        op.alter_column(
            'newspaper_summary',
            column,
            existing_type=sa.Text(),
            type_=sa.String(length=255),
            existing_nullable=True,
        )

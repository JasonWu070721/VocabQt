"""Add familiarity column to words table

Revision ID: 4714ba4ea347
Revises: e3e72c980409
Create Date: 2024-09-16 10:05:07.308652

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from utils.checks import column_exists

# revision identifiers, used by Alembic.
revision: str = "4714ba4ea347"
down_revision: Union[str, None] = "e3e72c980409"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if not column_exists("words", "familiarity"):
        op.add_column(
            "words",
            sa.Column("familiarity", sa.Integer(), nullable=False, server_default="0"),
        )


def downgrade() -> None:
    op.drop_column("words", "familiarity")

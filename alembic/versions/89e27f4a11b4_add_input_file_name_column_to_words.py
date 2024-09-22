"""Add input_file_name column to words

Revision ID: 89e27f4a11b4
Revises: f131ce5f9b07
Create Date: 2024-09-22 21:30:53.458832

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89e27f4a11b4'
down_revision: Union[str, None] = 'f131ce5f9b07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('words', 
                  sa.Column('input_file_name', sa.String()))


def downgrade() -> None:
    op.drop_column('words', 'input_file_name')

"""Rename input_file_name to input_file_id on words table

Revision ID: 134e72f0dc48
Revises: ab3822b22e06
Create Date: 2024-09-23 08:49:19.074694

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '134e72f0dc48'
down_revision: Union[str, None] = 'ab3822b22e06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('words', sa.Column('input_file_id', sa.Integer(), nullable=True))
    op.drop_column('words', 'input_file_name')


def downgrade() -> None:
    op.add_column('words', sa.Column('input_file_name', sa.Text()))
    op.drop_column('words', 'input_file_id')

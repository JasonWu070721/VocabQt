"""create user words

Revision ID: e3e72c980409
Revises: 
Create Date: 2024-09-12 11:35:34.173835

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = "e3e72c980409"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)

    if not inspector.has_table("words"):
        op.create_table(
            "words",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("word", sa.Text, nullable=False),
            sa.Column("cht", sa.Text, nullable=False),
            sa.Column("mp3_url", sa.Text, nullable=False),
            sa.Column(
                "created_at", sa.DateTime, server_default=sa.func.now(), nullable=False
            ),
            sa.Column(
                "updated_at",
                sa.DateTime,
                server_default=sa.func.now(),
                onupdate=sa.func.now(),
                nullable=False,
            ),
        )


def downgrade() -> None:
    op.drop_table("words")

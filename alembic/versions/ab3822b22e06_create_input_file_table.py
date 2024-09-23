"""Create input file table

Revision ID: ab3822b22e06
Revises: 89e27f4a11b4
Create Date: 2024-09-23 08:32:59.958569

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision: str = "ab3822b22e06"
down_revision: Union[str, None] = "89e27f4a11b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)

    if not inspector.has_table("input_files"):
        op.create_table(
            "input_files",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("file_name", sa.Text, nullable=False),
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

        op.execute("INSERT INTO input_files (file_name) VALUES ('All')")
        op.execute("INSERT INTO input_files (file_name) VALUES ('my_words')")


def downgrade() -> None:
    op.drop_table("input_files")

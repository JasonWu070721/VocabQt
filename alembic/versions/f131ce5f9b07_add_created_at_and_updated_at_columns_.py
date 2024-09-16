"""Add created_at and updated_at columns to words table

Revision ID: f131ce5f9b07
Revises: 4714ba4ea347
Create Date: 2024-09-16 10:41:51.681645

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f131ce5f9b07"
down_revision: Union[str, None] = "4714ba4ea347"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "words",
        sa.Column("created_at", sa.DateTime, nullable=True),
    )
    op.add_column(
        "words",
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=True,
        ),
    )

    op.execute("UPDATE words SET created_at = CURRENT_TIMESTAMP")
    op.execute("UPDATE words SET updated_at = CURRENT_TIMESTAMP")

    with op.batch_alter_table("words") as batch_op:
        batch_op.alter_column(
            "created_at", server_default=sa.func.now(), nullable=False
        )
        batch_op.alter_column(
            "updated_at",
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        )


def downgrade() -> None:
    op.drop_column("words", "created_at")
    op.drop_column("words", "updated_at")

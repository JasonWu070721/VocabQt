"""Update words table to link with input_files by file_name_id

Revision ID: a9cc3ec196c4
Revises: 134e72f0dc48
Create Date: 2024-09-23 11:31:06.254802

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "a9cc3ec196c4"
down_revision: Union[str, None] = "134e72f0dc48"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    result = bind.execute(
        text("SELECT id FROM input_files WHERE file_name = 'my_words'")
    )
    input_file_id = result.fetchone()[0]

    op.execute(f"UPDATE words SET input_file_id = {input_file_id}")


def downgrade() -> None:
    op.execute("UPDATE words SET input_file_id = NULL")

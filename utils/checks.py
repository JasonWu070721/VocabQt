from alembic import op
from sqlalchemy import inspect


def column_exists(table_name: str, column_name: str) -> bool:
    # Create an inspector to check the table's columns
    inspector = inspect(op.get_bind())
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns

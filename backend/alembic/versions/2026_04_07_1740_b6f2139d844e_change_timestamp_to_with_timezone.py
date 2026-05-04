"""change_timestamp_to_with_timezone

Revision ID: b6f2139d844e
Revises: 87a3c2dcce7e
Create Date: 2026-04-07 17:40:48.787116

"""

from typing import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b6f2139d844e"
down_revision: str | None = "87a3c2dcce7e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # users table
    op.execute(
        "ALTER TABLE users ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE"
    )
    op.execute(
        "ALTER TABLE users ALTER COLUMN last_login TYPE TIMESTAMP WITH TIME ZONE"
    )

    # user_preferences table
    op.execute(
        "ALTER TABLE user_preferences ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE"
    )
    op.execute(
        "ALTER TABLE user_preferences ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE"
    )

    # exchange_rates table
    op.execute(
        "ALTER TABLE exchange_rates ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE"
    )

    # interest_rates table
    op.execute(
        "ALTER TABLE interest_rates ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE"
    )

    # chat_messages table
    op.execute(
        "ALTER TABLE chat_messages ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE"
    )


def downgrade() -> None:
    # users table
    op.execute(
        "ALTER TABLE users ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE"
    )
    op.execute(
        "ALTER TABLE users ALTER COLUMN last_login TYPE TIMESTAMP WITHOUT TIME ZONE"
    )

    # user_preferences table
    op.execute(
        "ALTER TABLE user_preferences ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE"
    )
    op.execute(
        "ALTER TABLE user_preferences ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE"
    )

    # exchange_rates table
    op.execute(
        "ALTER TABLE exchange_rates ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE"
    )

    # interest_rates table
    op.execute(
        "ALTER TABLE interest_rates ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE"
    )

    # chat_messages table
    op.execute(
        "ALTER TABLE chat_messages ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE"
    )

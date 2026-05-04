"""Add jti column to refresh tokens

Revision ID: 003_add_jti
Revises: 002_add_refresh_tokens
Create Date: 2025-04-10 15:00:00.000000

"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003_add_jti"
down_revision: str | None = "002_add_refresh_tokens"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "refresh_tokens",
        sa.Column("jti", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.execute(
        """
        UPDATE refresh_tokens 
        SET jti = gen_random_uuid()
        WHERE jti IS NULL
        """
    )

    op.alter_column("refresh_tokens", "jti", nullable=False)

    op.create_index(op.f("ix_refresh_tokens_jti"), "refresh_tokens", ["jti"])


def downgrade() -> None:
    op.drop_index(op.f("ix_refresh_tokens_jti"), table_name="refresh_tokens")
    op.drop_column("refresh_tokens", "jti")

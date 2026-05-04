"""Add refresh tokens table

Revision ID: add_refresh_tokens
Revises:
Create Date: 2025-04-10 12:00:00.000000

"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002_add_refresh_tokens"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "refresh_tokens",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(255), unique=True, nullable=False),
        sa.Column("device_info", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked", sa.Boolean(), server_default="false"),
    )

    op.create_index(op.f("ix_refresh_tokens_user_id"), "refresh_tokens", ["user_id"])
    op.create_index(
        op.f("ix_refresh_tokens_token_hash"), "refresh_tokens", ["token_hash"]
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_refresh_tokens_token_hash"), table_name="refresh_tokens")
    op.drop_index(op.f("ix_refresh_tokens_user_id"), table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

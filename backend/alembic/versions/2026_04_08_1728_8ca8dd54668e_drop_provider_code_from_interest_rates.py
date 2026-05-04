"""drop_provider_code_from_interest_rates

Revision ID: 8ca8dd54668e
Revises: b6f2139d844e
Create Date: 2026-04-08 17:28:41.356901

"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8ca8dd54668e"
down_revision: str | None = "b6f2139d844e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("interest_rates", "provider_code")


def downgrade() -> None:
    op.add_column(
        "interest_rates", sa.Column("provider_code", sa.String(100), nullable=True)
    )

"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-04-07 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('is_verified', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
    )

    # Create magic_links table
    op.create_table(
        'magic_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('used', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
    )

    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('currency_pairs', postgresql.ARRAY(sa.String()), nullable=False, server_default=sa.text("ARRAY['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD', 'USD/CNY', 'USD/HKD']::text[]")),
        sa.Column('email_frequency', sa.String(20), server_default='daily'),
        sa.Column('alert_thresholds', postgresql.JSONB(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
    )

    # Create exchange_rates table
    op.create_table(
        'exchange_rates',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('base_currency', sa.String(3), nullable=False),
        sa.Column('target_currency', sa.String(3), nullable=False),
        sa.Column('rate', sa.Numeric(10, 6), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('source', sa.String(50), server_default='frankfurter'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
    )
    op.create_index('idx_exchange_rates_date', 'exchange_rates', ['date'])
    op.create_index('idx_exchange_rates_pair', 'exchange_rates', ['base_currency', 'target_currency'])

    # Create interest_rates table
    op.create_table(
        'interest_rates',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('country_code', sa.String(3), nullable=False),
        sa.Column('currency_code', sa.String(3), nullable=False),
        sa.Column('rate', sa.Numeric(5, 2), nullable=False),
        sa.Column('rate_type', sa.String(50), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('source', sa.String(50), server_default='dbnomics'),
        sa.Column('provider_code', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
    )
    op.create_index('idx_interest_rates_date', 'interest_rates', ['date'])
    op.create_index('idx_interest_rates_country', 'interest_rates', ['country_code'])

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
    )
    op.create_index('idx_chat_messages_user', 'chat_messages', ['user_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('idx_chat_messages_user', 'chat_messages')
    op.drop_table('chat_messages')
    
    op.drop_index('idx_interest_rates_country', 'interest_rates')
    op.drop_index('idx_interest_rates_date', 'interest_rates')
    op.drop_table('interest_rates')
    
    op.drop_index('idx_exchange_rates_pair', 'exchange_rates')
    op.drop_index('idx_exchange_rates_date', 'exchange_rates')
    op.drop_table('exchange_rates')
    
    op.drop_table('user_preferences')
    op.drop_table('magic_links')
    op.drop_table('users')
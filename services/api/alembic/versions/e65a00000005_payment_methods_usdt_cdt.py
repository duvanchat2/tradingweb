"""Linked payment methods and fixed USDT CDT terms.

Revision ID: e65a00000005
Revises: d54f00000004
"""
from alembic import op
import sqlalchemy as sa

revision = 'e65a00000005'
down_revision = 'd54f00000004'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'payment_methods',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('label', sa.String(length=80), nullable=False),
        sa.Column('holder_name', sa.String(length=160), nullable=False),
        sa.Column('bank_name', sa.String(length=120), nullable=True),
        sa.Column('account_type', sa.String(length=40), nullable=True),
        sa.Column('account_last4', sa.String(length=4), nullable=True),
        sa.Column('card_brand', sa.String(length=40), nullable=True),
        sa.Column('card_last4', sa.String(length=4), nullable=True),
        sa.Column('network', sa.String(length=64), nullable=True),
        sa.Column('wallet_address', sa.String(length=256), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.CheckConstraint("type IN ('bank','card','crypto')", name='payment_methods_type_check'),
    )
    op.create_index('ix_payment_methods_user_id', 'payment_methods', ['user_id'])
    op.add_column('payment_requests', sa.Column('payment_method_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_payment_requests_payment_method_id', 'payment_requests', 'payment_methods', ['payment_method_id'], ['id'])
    op.execute("UPDATE stake_plans SET currency='USDT', apy=20, term_days=365 WHERE is_active IS TRUE")


def downgrade():
    op.drop_constraint('fk_payment_requests_payment_method_id', 'payment_requests', type_='foreignkey')
    op.drop_column('payment_requests', 'payment_method_id')
    op.drop_index('ix_payment_methods_user_id', table_name='payment_methods')
    op.drop_table('payment_methods')

"""Store encrypted bank account numbers.

Revision ID: c13e00000009
Revises: b02d00000008
"""
from alembic import op
import sqlalchemy as sa

revision='c13e00000009'
down_revision='b02d00000008'
branch_labels=None
depends_on=None


def upgrade():
    op.add_column('payment_methods',sa.Column('bank_account_encrypted',sa.Text(),nullable=True))


def downgrade():
    op.drop_column('payment_methods','bank_account_encrypted')

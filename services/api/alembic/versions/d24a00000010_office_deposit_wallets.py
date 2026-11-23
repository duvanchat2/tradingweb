"""Scope deposit addresses to offices.

Existing addresses remain unassigned so they cannot appear in a client's
wallet until a superworker explicitly assigns them to an office.

Revision ID: d24a00000010
Revises: c13e00000009
"""
from alembic import op
import sqlalchemy as sa

revision='d24a00000010'
down_revision='c13e00000009'
branch_labels=None
depends_on=None


def upgrade():
    op.add_column('wallets_deposit',sa.Column('office_id',sa.Integer(),nullable=True))
    op.create_foreign_key('fk_wallets_deposit_office_id','wallets_deposit','offices',['office_id'],['id'])
    op.create_unique_constraint('uq_deposit_wallet_office_currency_network','wallets_deposit',['office_id','currency','network'])


def downgrade():
    op.drop_constraint('uq_deposit_wallet_office_currency_network','wallets_deposit',type_='unique')
    op.drop_constraint('fk_wallets_deposit_office_id','wallets_deposit',type_='foreignkey')
    op.drop_column('wallets_deposit','office_id')

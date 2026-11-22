"""Add the supported multi-currency CDT catalog.

Revision ID: b02d00000008
Revises: a91d00000007
"""
from alembic import op

revision='b02d00000008'
down_revision='a91d00000007'
branch_labels=None
depends_on=None

PLANS=(
    ('BTC','4.50','0.001','30'),
    ('BTC','8.20','0.005','30'),
    ('ETH','5.00','0.01','30'),
    ('ETH','12.50','0.05','60'),
    ('USDT','5.50','10','30'),
    ('USDT','6.80','100','30'),
    ('USDT','9.50','500','90'),
)

def upgrade():
    for currency,apy,minimum,days in PLANS:
        op.execute(f"""INSERT INTO stake_plans(currency,apy,min_amount,term_days,is_active,created_at)
        SELECT '{currency}',{apy},{minimum},{days},true,NOW() WHERE NOT EXISTS(
          SELECT 1 FROM stake_plans WHERE currency='{currency}' AND apy={apy} AND min_amount={minimum} AND term_days={days}
        )""")

def downgrade():
    for currency,apy,minimum,days in PLANS:
        op.execute(f"DELETE FROM stake_plans WHERE currency='{currency}' AND apy={apy} AND min_amount={minimum} AND term_days={days}")

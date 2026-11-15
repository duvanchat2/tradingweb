"""Paper trading kinds, order expiry, escrow and explicit simulated execution."""
from alembic import op
import sqlalchemy as sa

revision = 'b42e1200f002'
down_revision = '7543f0225248'
branch_labels = None
depends_on = None

OLD_KINDS = "'deposit','withdrawal','credit','debit','swap_in','swap_out','stake_lock','stake_yield','fee','correction'"

def upgrade():
    op.drop_constraint('accounts_type_check', 'accounts', type_='check')
    op.create_check_constraint('accounts_type_check', 'accounts', "type IN ('main','staking','system','escrow')")
    op.drop_constraint('transactions_kind_check', 'transactions', type_='check')
    op.create_check_constraint('transactions_kind_check', 'transactions', "kind IN ("+OLD_KINDS+",'trade','withdrawal_lock')")
    op.drop_constraint('orders_status_check', 'orders', type_='check')
    op.create_check_constraint('orders_status_check', 'orders', "status IN ('open','filled','cancelled','expired')")
    op.add_column('orders', sa.Column('fee_amount', sa.Numeric(28,8), nullable=True))
    op.add_column('orders', sa.Column('fee_currency', sa.String(10), nullable=True))
    op.add_column('payment_requests', sa.Column('destination_address', sa.String(256), nullable=True))
    op.add_column('payment_requests', sa.Column('execution_status', sa.String(16), nullable=False, server_default='simulated'))
    op.create_check_constraint('payment_requests_demo_only', 'payment_requests', "execution_status = 'simulated'")

def downgrade():
    # Refuse destructive rollback if phase-2 data uses the extended vocabulary.
    # Existing escrow accounts/trades/expired orders must be retained or archived first.
    op.drop_constraint('payment_requests_demo_only', 'payment_requests', type_='check')
    op.drop_column('payment_requests', 'execution_status')
    op.drop_column('payment_requests', 'destination_address')
    op.drop_column('orders', 'fee_currency')
    op.drop_column('orders', 'fee_amount')
    op.drop_constraint('orders_status_check', 'orders', type_='check')
    op.create_check_constraint('orders_status_check', 'orders', "status IN ('open','filled','cancelled')")
    op.drop_constraint('transactions_kind_check', 'transactions', type_='check')
    op.create_check_constraint('transactions_kind_check', 'transactions', 'kind IN ('+OLD_KINDS+')')
    op.drop_constraint('accounts_type_check', 'accounts', type_='check')
    op.create_check_constraint('accounts_type_check', 'accounts', "type IN ('main','staking','system')")

"""Audit-backed idempotency and economic resolution independent of review state."""
from alembic import op
import sqlalchemy as sa
revision='c3a000000003'
down_revision='b42e1200f002'
branch_labels=None
depends_on=None

def upgrade():
    op.add_column('audit_log',sa.Column('idempotency_key',sa.String(128),nullable=True))
    op.add_column('audit_log',sa.Column('request_hash',sa.String(64),nullable=True))
    op.create_unique_constraint('uq_audit_actor_idempotency','audit_log',['actor_id','idempotency_key'])
    op.add_column('payment_requests',sa.Column('ledger_resolution',sa.String(16),nullable=False,server_default='unsettled'))
    op.execute("UPDATE payment_requests SET ledger_resolution=CASE WHEN method='simulated-withdrawal' THEN 'paid' ELSE 'credited' END WHERE status='approved'")
    op.execute("UPDATE payment_requests SET ledger_resolution='released' WHERE method='simulated-withdrawal' AND status='rejected'")

def downgrade():
    op.drop_column('payment_requests','ledger_resolution')
    op.drop_constraint('uq_audit_actor_idempotency','audit_log',type_='unique')
    op.drop_column('audit_log','request_hash')
    op.drop_column('audit_log','idempotency_key')

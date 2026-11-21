"""KYC image storage, office isolation and feature controls.

Revision ID: f76b00000006
Revises: e65a00000005
"""
from alembic import op
import sqlalchemy as sa

revision='f76b00000006'
down_revision='e65a00000005'
branch_labels=None
depends_on=None

def upgrade():
    op.create_table('offices',
        sa.Column('name',sa.String(160),nullable=False),
        sa.Column('token_secret',sa.String(64),nullable=False),
        sa.Column('trading_enabled',sa.Boolean(),nullable=False,server_default=sa.true()),
        sa.Column('swap_enabled',sa.Boolean(),nullable=False,server_default=sa.true()),
        sa.Column('withdrawals_enabled',sa.Boolean(),nullable=False,server_default=sa.true()),
        sa.Column('is_active',sa.Boolean(),nullable=False,server_default=sa.true()),
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.UniqueConstraint('name'),sa.UniqueConstraint('token_secret'))
    op.execute("""INSERT INTO offices (id,name,token_secret,created_at)
        SELECT DISTINCT office_id, 'Oficina heredada ' || office_id,
        md5(random()::text || office_id::text) || md5(clock_timestamp()::text), now()
        FROM users WHERE office_id IS NOT NULL""")
    op.execute("SELECT setval(pg_get_serial_sequence('offices','id'), COALESCE((SELECT max(id) FROM offices),1), true)")
    op.alter_column('users','registration_code',type_=sa.String(16),existing_type=sa.String(6))
    op.create_foreign_key('fk_users_office_id','users','offices',['office_id'],['id'])
    op.add_column('kyc_documents',sa.Column('original_name',sa.String(255),nullable=True))
    op.add_column('kyc_documents',sa.Column('mime_type',sa.String(64),nullable=True))
    op.add_column('kyc_documents',sa.Column('file_data',sa.LargeBinary(),nullable=True))

def downgrade():
    op.drop_column('kyc_documents','file_data');op.drop_column('kyc_documents','mime_type');op.drop_column('kyc_documents','original_name')
    op.drop_constraint('fk_users_office_id','users',type_='foreignkey')
    op.alter_column('users','registration_code',type_=sa.String(6),existing_type=sa.String(16))
    op.drop_table('offices')

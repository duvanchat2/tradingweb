"""Add registration profile metadata.

Revision ID: d54f00000004
Revises: c3a000000003
"""

from alembic import op
import sqlalchemy as sa

revision = 'd54f00000004'
down_revision = 'c3a000000003'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('registration_code', sa.String(length=6), nullable=True))
    op.create_index(op.f('ix_users_registration_code'), 'users', ['registration_code'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_users_registration_code'), table_name='users')
    op.drop_column('users', 'registration_code')

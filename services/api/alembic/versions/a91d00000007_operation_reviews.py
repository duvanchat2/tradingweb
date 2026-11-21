"""Admin-reviewed swap and stake requests.

Revision ID: a91d00000007
Revises: f76b00000006
"""
from alembic import op
import sqlalchemy as sa

revision = 'a91d00000007'
down_revision = 'f76b00000006'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('swaps_status_check', 'swaps', type_='check')
    op.execute("UPDATE swaps SET status='approved' WHERE status='completed'")
    op.create_check_constraint('swaps_status_check', 'swaps', "status IN ('pending','approved','rejected')")
    op.add_column('swaps', sa.Column('staff_note', sa.Text(), nullable=True))
    op.add_column('swaps', sa.Column('reviewer_id', sa.Integer(), nullable=True))
    op.add_column('swaps', sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key('fk_swaps_reviewer_id', 'swaps', 'users', ['reviewer_id'], ['id'])

    op.drop_constraint('stake_positions_status_check', 'stake_positions', type_='check')
    op.create_check_constraint('stake_positions_status_check', 'stake_positions', "status IN ('pending','active','rejected','closed')")
    op.alter_column('stake_positions', 'opened_at', existing_type=sa.DateTime(timezone=True), nullable=True)
    op.alter_column('stake_positions', 'closes_at', existing_type=sa.DateTime(timezone=True), nullable=True)
    op.add_column('stake_positions', sa.Column('staff_note', sa.Text(), nullable=True))
    op.add_column('stake_positions', sa.Column('reviewer_id', sa.Integer(), nullable=True))
    op.add_column('stake_positions', sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key('fk_stake_positions_reviewer_id', 'stake_positions', 'users', ['reviewer_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_stake_positions_reviewer_id', 'stake_positions', type_='foreignkey')
    op.drop_column('stake_positions', 'reviewed_at')
    op.drop_column('stake_positions', 'reviewer_id')
    op.drop_column('stake_positions', 'staff_note')
    op.execute("DELETE FROM stake_positions WHERE status IN ('pending','rejected')")
    op.alter_column('stake_positions', 'closes_at', existing_type=sa.DateTime(timezone=True), nullable=False)
    op.alter_column('stake_positions', 'opened_at', existing_type=sa.DateTime(timezone=True), nullable=False)
    op.drop_constraint('stake_positions_status_check', 'stake_positions', type_='check')
    op.create_check_constraint('stake_positions_status_check', 'stake_positions', "status IN ('active','closed')")

    op.drop_constraint('fk_swaps_reviewer_id', 'swaps', type_='foreignkey')
    op.drop_column('swaps', 'reviewed_at')
    op.drop_column('swaps', 'reviewer_id')
    op.drop_column('swaps', 'staff_note')
    op.execute("DELETE FROM swaps WHERE status IN ('pending','rejected')")
    op.drop_constraint('swaps_status_check', 'swaps', type_='check')
    op.execute("UPDATE swaps SET status='completed' WHERE status='approved'")
    op.create_check_constraint('swaps_status_check', 'swaps', "status IN ('completed','failed')")

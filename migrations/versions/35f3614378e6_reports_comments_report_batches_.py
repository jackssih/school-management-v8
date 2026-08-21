"""report_batches: report_scope

Revision ID: d7e8f9a0b1c2
Revises: e2f4a7c1d9b3
Create Date: 2026-08-20 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35f3614378e6'
down_revision = 'a5382b7b6d55'
branch_labels = None
depends_on = None


def upgrade():
    # Guarded with an existence check: some installs already picked up this
    # column manually (or via an earlier copy of this file) before it was
    # accidentally overwritten with a duplicate of the 35f3614378e6 revision.
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('report_batches')]
    if 'report_scope' not in columns:
        with op.batch_alter_table('report_batches', schema=None) as batch_op:
            batch_op.add_column(sa.Column('report_scope', sa.String(length=40), nullable=True))


def downgrade():
    with op.batch_alter_table('report_batches', schema=None) as batch_op:
        batch_op.drop_column('report_scope')
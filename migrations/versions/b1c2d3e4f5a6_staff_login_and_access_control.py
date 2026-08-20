"""staff: login credentials, access control, theme preference

Revision ID: b1c2d3e4f5a6
Revises: f1a6c9d2e3b7
Create Date: 2026-08-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5a6'
down_revision = 'f1a6c9d2e3b7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('staff', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(length=255), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('must_change_password', sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column('theme', sa.String(length=10), nullable=False, server_default='light'))


def downgrade():
    with op.batch_alter_table('staff', schema=None) as batch_op:
        batch_op.drop_column('theme')
        batch_op.drop_column('is_active')
        batch_op.drop_column('must_change_password')
        batch_op.drop_column('password_hash')

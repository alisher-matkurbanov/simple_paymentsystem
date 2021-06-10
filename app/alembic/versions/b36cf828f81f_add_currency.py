"""add currency

Revision ID: b36cf828f81f
Revises: 
Create Date: 2021-06-10 12:39:28.154217

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b36cf828f81f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
    'currency',
    sa.Column('code', sa.String(length=3), nullable=False),
    sa.PrimaryKeyConstraint('code')
    )
    op.execute("INSERT INTO currency VALUES ('USD') ON CONFLICT DO NOTHING;")


def downgrade():
    op.drop_table('currency')


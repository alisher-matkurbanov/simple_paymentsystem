"""Add USD currency

Revision ID: 164e78eca0e1
Revises: 3ddd257b402d
Create Date: 2021-06-10 00:11:11.802464

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '164e78eca0e1'
down_revision = '3ddd257b402d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("INSERT INTO currency(code) VALUES ('USD') ON CONFLICT DO NOTHING")


def downgrade():
    op.execute("DELETE FROM currency WHERE code = 'USD'")

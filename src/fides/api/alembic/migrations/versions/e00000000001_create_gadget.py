"""Create the gadget table

Revision ID: e00000000001
Revises: d00000000001
Create Date: 2026-05-01 09:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "e00000000001"
down_revision = "d00000000001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("gadget", sa.Column("id", sa.String(), primary_key=True))


def downgrade():
    op.drop_table("gadget")

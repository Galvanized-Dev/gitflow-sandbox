"""Create the widget table

Revision ID: a00000000001
Revises:
Create Date: 2026-01-01 09:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "a00000000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "widget",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
    )


def downgrade():
    op.drop_table("widget")

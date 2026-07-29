"""Add widget.color

Revision ID: a00000000002
Revises: a00000000001
Create Date: 2026-01-02 09:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "a00000000002"
down_revision = "a00000000001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("widget", sa.Column("color", sa.String(), nullable=True))


def downgrade():
    op.drop_column("widget", "color")

"""Add widget.label

Revision ID: f00000000001
Revises: d00000000001
Create Date: 2026-05-02 09:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "f00000000001"
down_revision = "d00000000001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("widget", sa.Column("label", sa.String(), nullable=True))


def downgrade():
    op.drop_column("widget", "label")

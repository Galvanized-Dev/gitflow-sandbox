"""Add widget.size  [FIXTURE: the patch fix, authored on dev]

Its parent is b00000000002, which is UNRELEASED. Cherry-picked onto a branch cut from
a release tag, that ancestor is absent and this migration cannot apply — a missing
ancestor, not a multiple-heads case. This is the file the downrev preflight flags.

Revision ID: c00000000001
Revises: b00000000002
Create Date: 2026-03-01 09:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "c00000000001"
down_revision = "a00000000002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("widget", sa.Column("size", sa.String(), nullable=True))


def downgrade():
    op.drop_column("widget", "size")

"""Create the shadow schema  [FIXTURE: unreleased dev chain, part 1]

Revision ID: b00000000001
Revises: a00000000002
Create Date: 2026-02-01 09:00:00.000000

"""

from alembic import op

revision = "b00000000001"
down_revision = "a00000000002"
branch_labels = None
depends_on = None


def upgrade():
    # Something LATER migrations depend on existing. This is what makes ordering
    # (not just parentage) observable: a child that runs before this fails hard.
    op.execute("CREATE SCHEMA IF NOT EXISTS shadow")


def downgrade():
    op.execute("DROP SCHEMA IF EXISTS shadow CASCADE")

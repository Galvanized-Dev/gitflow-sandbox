"""Create shadow.audit  [FIXTURE: unreleased dev chain, part 2]

Revision ID: b00000000002
Revises: b00000000001
Create Date: 2026-02-02 09:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "b00000000002"
down_revision = "b00000000001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "audit",
        sa.Column("id", sa.String(), primary_key=True),
        schema="shadow",
    )


def downgrade():
    op.drop_table("audit", schema="shadow")

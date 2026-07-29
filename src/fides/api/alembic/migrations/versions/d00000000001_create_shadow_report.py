"""Create shadow.report  [FIXTURE: a child of the patched revision]

Child of c00000000001 AND dependent on the `shadow` schema that the buried chain
(b00000000001) creates. This is the scenario-8 shape: if the sprint joins the buried
chain at the tip instead of before this revision, this runs first and dies with
`schema "shadow" does not exist`. A static down_revision check cannot see that; only
running it on Postgres can.

Revision ID: d00000000001
Revises: c00000000001
Create Date: 2026-04-01 09:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "d00000000001"
down_revision = "b990fb343824"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "report",
        sa.Column("id", sa.String(), primary_key=True),
        schema="shadow",
    )


def downgrade():
    op.drop_table("report", schema="shadow")

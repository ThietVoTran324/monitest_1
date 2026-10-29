"""one open incident per monitor (partial unique)

Revision ID: c2d3e4f5a6b7
Revises: b3c4d5e6f7a8
Create Date: 2026-10-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c2d3e4f5a6b7"
down_revision: str | None = "b3c4d5e6f7a8"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    # Keep newest OPEN per monitor; close the rest before unique index.
    op.execute(
        sa.text(
            """
            WITH ranked AS (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        PARTITION BY monitor_id
                        ORDER BY opened_at DESC, created_at DESC, id DESC
                    ) AS rn
                FROM incidents
                WHERE status = 'open'
            )
            UPDATE incidents AS i
            SET
                status = 'closed',
                closed_at = COALESCE(i.closed_at, NOW()),
                close_reason = COALESCE(
                    i.close_reason,
                    'Closed by Sprint2 unique-open migration'
                )
            FROM ranked AS r
            WHERE i.id = r.id AND r.rn > 1
            """
        )
    )
    op.create_index(
        "uq_incidents_one_open_per_monitor",
        "incidents",
        ["monitor_id"],
        unique=True,
        postgresql_where=sa.text("status = 'open'"),
    )


def downgrade() -> None:
    op.drop_index("uq_incidents_one_open_per_monitor", table_name="incidents")

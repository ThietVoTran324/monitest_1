"""email outbox + users.is_admin + monitor backoff overrides

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-10-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d3e4f5a6b7c8"
down_revision: str | None = "c2d3e4f5a6b7"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "monitors",
        sa.Column("alert_outbox_max_attempts", sa.Integer(), nullable=True),
    )
    op.add_column(
        "monitors",
        sa.Column("alert_outbox_backoff_seconds", sa.String(length=255), nullable=True),
    )

    outbox_status = sa.Enum(
        "pending",
        "sent",
        "failed",
        name="email_outbox_status",
    )
    outbox_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "email_outbox",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("monitor_id", sa.Uuid(), nullable=False),
        sa.Column("incident_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("to_email", sa.String(length=320), nullable=False),
        sa.Column("status", outbox_status, nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["monitor_id"], ["monitors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_outbox_monitor_id", "email_outbox", ["monitor_id"])
    op.create_index("ix_email_outbox_status_next", "email_outbox", ["status", "next_attempt_at"])


def downgrade() -> None:
    op.drop_index("ix_email_outbox_status_next", table_name="email_outbox")
    op.drop_index("ix_email_outbox_monitor_id", table_name="email_outbox")
    op.drop_table("email_outbox")
    sa.Enum(name="email_outbox_status").drop(op.get_bind(), checkfirst=True)
    op.drop_column("monitors", "alert_outbox_backoff_seconds")
    op.drop_column("monitors", "alert_outbox_max_attempts")
    op.drop_column("users", "is_admin")

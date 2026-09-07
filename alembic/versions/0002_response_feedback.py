"""Add auditable response feedback and review records."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_response_feedback"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "response_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("review_status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("model_version", sa.String(150), nullable=False),
        sa.Column("prompt_version", sa.String(80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_response_feedback_user_id", "response_feedback", ["user_id"])
    op.create_index("ix_response_feedback_conversation_id", "response_feedback", ["conversation_id"])


def downgrade() -> None:
    op.drop_index("ix_response_feedback_conversation_id", table_name="response_feedback")
    op.drop_index("ix_response_feedback_user_id", table_name="response_feedback")
    op.drop_table("response_feedback")
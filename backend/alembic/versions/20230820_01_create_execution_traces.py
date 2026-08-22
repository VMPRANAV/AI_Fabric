"""Create execution_traces table

Revision ID: 20230820_01_create_execution_traces
Revises: None
Create Date: 2026-08-20 14:20:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20230820_01_create_execution_traces"
branch_labels = None
depends_on = None
down_revision = None
def upgrade() -> None:
    op.create_table(
        "execution_traces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("request_id", sa.String(length=36), nullable=False, unique=True),
        sa.Column("strategy", sa.String(length=50), nullable=True),
        sa.Column("task_type", sa.String(length=50), nullable=True),
        sa.Column("selected_model", sa.String(length=100), nullable=True),
        sa.Column("prompt_version", sa.String(length=50), nullable=True),
        sa.Column("start_timestamp", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("end_timestamp", sa.DateTime(), nullable=True),
        sa.Column("total_latency_ms", sa.Float(), nullable=True),
        sa.Column("input_tokens", sa.Float(), nullable=True),
        sa.Column("output_tokens", sa.Float(), nullable=True),
        sa.Column("total_tokens", sa.Float(), nullable=True),
        sa.Column("cost_usd", sa.Float(), nullable=True),
        sa.Column("tool_success", sa.Boolean(), nullable=True),
        sa.Column("model_success", sa.Boolean(), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("reward", sa.Float(), nullable=True),
        sa.Column("state_vector", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("stages", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(op.f("ix_execution_traces_request_id"), "execution_traces", ["request_id"], unique=True)

def downgrade() -> None:
    op.drop_index(op.f("ix_execution_traces_request_id"), table_name="execution_traces")
    op.drop_table("execution_traces")

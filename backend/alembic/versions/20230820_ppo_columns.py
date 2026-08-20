from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20230820_ppo_columns"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('routing_decisions', sa.Column('policy', sa.String(), nullable=True))
    op.add_column('routing_decisions', sa.Column('action', sa.Integer(), nullable=True))
    op.add_column('routing_decisions', sa.Column('reward', sa.Float(), nullable=True))
    op.add_column('routing_decisions', sa.Column('state_vector', sa.JSON(), nullable=True))
    op.add_column('routing_decisions', sa.Column('quality', sa.Float(), nullable=True))
    op.add_column('routing_decisions', sa.Column('latency_ms', sa.Float(), nullable=True))
    op.add_column('routing_decisions', sa.Column('cost', sa.Float(), nullable=True))
    op.add_column('routing_decisions', sa.Column('tool_success', sa.Boolean(), nullable=True))

def downgrade():
    op.drop_column('routing_decisions', 'tool_success')
    op.drop_column('routing_decisions', 'cost')
    op.drop_column('routing_decisions', 'latency_ms')
    op.drop_column('routing_decisions', 'quality')
    op.drop_column('routing_decisions', 'state_vector')
    op.drop_column('routing_decisions', 'reward')
    op.drop_column('routing_decisions', 'action')
    op.drop_column('routing_decisions', 'policy')

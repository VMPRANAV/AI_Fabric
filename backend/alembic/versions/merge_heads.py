"""merge independent heads

Revision ID: merge_heads_001
Revises: 20230820_01_create_execution_traces, 20230820_ppo_columns
Create Date: 2026-08-22

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'merge_heads_001'
down_revision: Union[tuple[str, ...], str, None] = ('20230820_01_create_execution_traces', '20230820_ppo_columns')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
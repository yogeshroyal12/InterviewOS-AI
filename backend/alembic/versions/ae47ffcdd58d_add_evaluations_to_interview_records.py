"""add evaluations to interview records

Revision ID: ae47ffcdd58d
Revises: f0ab39892cd1
Create Date: 2026-10-27 14:12:19.379038

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae47ffcdd58d'
down_revision: Union[str, Sequence[str], None] = 'f0ab39892cd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('interview_records', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('evaluations_json', sa.String(), nullable=False, server_default='[]')
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('interview_records', schema=None) as batch_op:
        batch_op.drop_column('evaluations_json')
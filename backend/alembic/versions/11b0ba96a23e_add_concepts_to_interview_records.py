"""add concepts to interview records

Revision ID: 11b0ba96a23e
Revises: ae47ffcdd58d
Create Date: 2026-10-27 15:05:02.623712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11b0ba96a23e'
down_revision: Union[str, Sequence[str], None] = 'ae47ffcdd58d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('interview_records', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('concepts_json', sa.String(), nullable=False, server_default='[]')
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('interview_records', schema=None) as batch_op:
        batch_op.drop_column('concepts_json')
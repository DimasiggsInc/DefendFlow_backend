"""empty message

Revision ID: b5af12afadc7
Revises: 62397d15f083
Create Date: 2026-06-06 20:58:21.118457

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = 'b5af12afadc7'
down_revision: Union[str, Sequence[str], None] = '62397d15f083'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

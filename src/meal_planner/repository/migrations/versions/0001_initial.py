"""Initial revision

Revision ID: 0001_initial
Revises: 
Create Date: 2026-03-16 00:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply initial schema.

    This revision intentionally does not create any application-specific tables.
    It provides a starting point for incremental schema migrations.
    """


def downgrade() -> None:
    """Revert initial schema."""
    pass

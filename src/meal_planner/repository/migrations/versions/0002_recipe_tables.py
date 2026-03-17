"""Add recipe tables

Revision ID: 0002_recipe_tables
Revises: 0001_initial
Create Date: 2026-03-17 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = "0002_recipe_tables"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply recipe schema."""
    # Create recipe state enum-like table for SQLite compatibility
    op.create_table(
        "recipe",
        sa.Column("id", sa.String(36), nullable=False, primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=True, index=True),
        sa.Column("title", sa.String(200), nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "state",
            sa.String(20),
            nullable=False,
            default="draft",
            index=True,
        ),
        sa.Column("base_servings", sa.Integer(), nullable=False, default=1),
        sa.Column("prep_time_minutes", sa.Integer(), nullable=True),
        sa.Column("cook_time_minutes", sa.Integer(), nullable=True),
        sa.Column(
            "parent_recipe_id",
            sa.String(36),
            sa.ForeignKey("recipe.id"),
            nullable=True,
            index=True,
        ),
        sa.Column("version_label", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Create recipe_ingredient table
    op.create_table(
        "recipe_ingredient",
        sa.Column("id", sa.String(36), nullable=False, primary_key=True),
        sa.Column(
            "recipe_id",
            sa.String(36),
            sa.ForeignKey("recipe.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("food_entry_id", sa.String(36), nullable=True, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("amount", sa.Numeric(10, 3), nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("to_taste", sa.Boolean(), nullable=False, default=False),
        sa.Column("optional", sa.Boolean(), nullable=False, default=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, default=0, index=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Create recipe_note table
    op.create_table(
        "recipe_note",
        sa.Column("id", sa.String(36), nullable=False, primary_key=True),
        sa.Column(
            "recipe_id",
            sa.String(36),
            sa.ForeignKey("recipe.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Revert recipe schema."""
    op.drop_table("recipe_note")
    op.drop_table("recipe_ingredient")
    op.drop_table("recipe")

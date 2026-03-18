"""Recipe and RecipeIngredient ORM models."""

from __future__ import annotations

import uuid
from enum import Enum
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import Boolean, Column, Enum as SQLEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base


class RecipeState(str, Enum):
    """Recipe state enumeration."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    INCOMPLETE = "incomplete"
    FINALIZED = "finalized"


class Recipe(Base):
    """Represents a homemade recipe with structured or draft content."""

    __tablename__ = "recipe"
    __allow_unmapped__ = True

    user_id: str | None = Column(String(36), nullable=True, index=True)
    title: str = Column(String(200), nullable=False, index=True)
    description: str | None = Column(Text, nullable=True)
    state: RecipeState = Column(
        SQLEnum(RecipeState), default=RecipeState.DRAFT, nullable=False, index=True
    )
    base_servings: int = Column(Integer, nullable=False, default=1)
    prep_time_minutes: int | None = Column(Integer, nullable=True)
    cook_time_minutes: int | None = Column(Integer, nullable=True)
    parent_recipe_id: str | None = Column(
        String(36), ForeignKey("recipe.id"), nullable=True, index=True
    )
    version_label: str | None = Column(String(100), nullable=True)

    # Relationships
    ingredients: list[RecipeIngredient] = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
        foreign_keys="RecipeIngredient.recipe_id",
    )
    notes: list[RecipeNote] = relationship(
        "RecipeNote",
        back_populates="recipe",
        cascade="all, delete-orphan",
        foreign_keys="RecipeNote.recipe_id",
    )
    # versions: list[Recipe] = relationship(
    #     "Recipe",
    #     remote_side=id,
    #     backref="parent",
    #     cascade="all, delete-orphan",
    # )

    def __repr__(self) -> str:
        return f"<Recipe {self.title!r} (state={self.state})>"


class RecipeIngredient(Base):
    """Links ingredients to recipes with amounts and nutrition."""

    __tablename__ = "recipe_ingredient"
    __allow_unmapped__ = True

    recipe_id: str = Column(String(36), ForeignKey("recipe.id"), nullable=False, index=True)
    food_entry_id: str | None = Column(
        String(36), ForeignKey("food_entry.id"), nullable=True, index=True
    )
    name: str = Column(String(100), nullable=False)
    amount: Decimal | None = Column(Numeric(10, 3), nullable=True)
    unit: str | None = Column(String(50), nullable=True)
    to_taste: bool = Column(Boolean, default=False, nullable=False)
    optional: bool = Column(Boolean, default=False, nullable=False)
    notes: str | None = Column(Text, nullable=True)
    sort_order: int = Column(Integer, nullable=False, default=0, index=True)

    # Relationships
    recipe: Recipe = relationship(
        "Recipe", back_populates="ingredients", foreign_keys=[recipe_id]
    )

    def __repr__(self) -> str:
        return f"<RecipeIngredient {self.name} in {self.recipe_id}>"


class RecipeNote(Base):
    """Stores user notes about recipes."""

    __tablename__ = "recipe_note"
    __allow_unmapped__ = True

    recipe_id: str = Column(String(36), ForeignKey("recipe.id"), nullable=False, index=True)
    text: str = Column(Text, nullable=False)

    # Relationships  
    recipe: Recipe = relationship(
        "Recipe", back_populates="notes", foreign_keys=[recipe_id]
    )

    def __repr__(self) -> str:
        return f"<RecipeNote on recipe {self.recipe_id}>"



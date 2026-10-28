"""LeftoverBatch and MealPlanEntry ORM models for meal planning."""

from __future__ import annotations

from enum import Enum

from sqlalchemy import Boolean, Column, Date, Enum as SQLEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class MealSlot(str, Enum):
    """Meal slot enumeration."""

    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class MealPlanEntry(Base):
    """A planned meal on a specific day."""

    __tablename__ = "meal_plan_entry"
    __allow_unmapped__ = True

    date = Column(Date, nullable=False, index=True)
    meal_slot: str = Column(SQLEnum(MealSlot), nullable=False, index=True)
    recipe_id: str = Column(String(36), ForeignKey("recipe.id"), nullable=False, index=True)
    servings = Column(Numeric(10, 2), nullable=False, default=1.0)
    batch_id: str | None = Column(String(36), ForeignKey("leftover_batch.id"), nullable=True, index=True)
    profile_id: str | None = Column(String(36), ForeignKey("profile.id"), nullable=True, index=True)
    notes: str | None = Column(Text, nullable=True)

    # Relationships
    recipe = relationship("Recipe", foreign_keys=[recipe_id])
    batch = relationship("LeftoverBatch", foreign_keys=[batch_id])
    profile = relationship("Profile", foreign_keys=[profile_id])

    def __repr__(self) -> str:
        return f"<MealPlanEntry {self.date} {self.meal_slot} recipe={self.recipe_id}>"


class LeftoverBatch(Base):
    """Tracks a prepared batch of food with remaining servings."""

    __tablename__ = "leftover_batch"
    __allow_unmapped__ = True

    recipe_id: str = Column(String(36), ForeignKey("recipe.id"), nullable=False, index=True)
    initial_servings: int = Column(Integer, nullable=False)
    servings_remaining: int = Column(Integer, nullable=False)
    prepared_date = Column(Date, nullable=False)

    # Relationships
    recipe = relationship("Recipe", foreign_keys=[recipe_id])

    def consume(self, servings: int = 1) -> int:
        """Consume servings from the batch. Returns remaining servings."""
        self.servings_remaining = max(0, self.servings_remaining - servings)
        if self.servings_remaining == 0:
            self.soft_delete()
        return self.servings_remaining

    def __repr__(self) -> str:
        return f"<LeftoverBatch recipe={self.recipe_id} remaining={self.servings_remaining}/{self.initial_servings}>"

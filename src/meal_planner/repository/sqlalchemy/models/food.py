"""FoodEntry and NutritionRecord ORM models."""

from __future__ import annotations

from enum import Enum

from sqlalchemy import Boolean, Column, Enum as SQLEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class FoodSourceType(str, Enum):
    """Source of the food entry data."""

    USDA = "usda"
    OPEN_FOOD_FACTS = "open_food_facts"
    BARCODE = "barcode"
    USER_CREATED = "user_created"
    CALCULATED = "calculated"


class NutritionSourceType(str, Enum):
    """Source/provenance of nutrition data on a NutritionRecord."""

    LABEL = "label"
    BARCODE = "barcode"
    USER_CONFIRMED = "user_confirmed"
    ESTIMATED = "estimated"
    CALCULATED = "calculated"


class FoodEntry(Base):
    """Represents a food item in the local ingredient library."""

    __tablename__ = "food_entry"
    __allow_unmapped__ = True

    user_id: str | None = Column(String(36), nullable=True, index=True)
    name: str = Column(String(200), nullable=False, index=True)
    brand: str | None = Column(String(200), nullable=True)
    category: str | None = Column(String(100), nullable=True)
    source_type: FoodSourceType = Column(
        SQLEnum(FoodSourceType), nullable=False, default=FoodSourceType.USER_CREATED
    )
    source_id: str | None = Column(String(200), nullable=True)
    is_custom: bool = Column(Boolean, default=False, nullable=False)

    # Relationships
    nutrition_records: list[NutritionRecord] = relationship(
        "NutritionRecord",
        back_populates="food_entry",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<FoodEntry {self.name!r} ({self.source_type})>"


class NutritionRecord(Base):
    """Contains nutrition data for a FoodEntry."""

    __tablename__ = "nutrition_record"
    __allow_unmapped__ = True

    food_entry_id: str = Column(
        String(36), ForeignKey("food_entry.id"), nullable=False, index=True
    )

    # Serving info
    serving_size: float = Column(Numeric(10, 3), nullable=False)
    serving_unit: str = Column(String(50), nullable=False)

    # Required macros
    calories: float = Column(Numeric(10, 2), nullable=False, default=0)
    protein_g: float = Column(Numeric(10, 2), nullable=False, default=0)
    carbohydrates_g: float = Column(Numeric(10, 2), nullable=False, default=0)
    fat_g: float = Column(Numeric(10, 2), nullable=False, default=0)
    added_sugar_g: float = Column(Numeric(10, 2), nullable=False, default=0)

    # Optional extended nutrients
    fiber_g: float | None = Column(Numeric(10, 2), nullable=True)
    total_sugar_g: float | None = Column(Numeric(10, 2), nullable=True)
    sodium_mg: float | None = Column(Numeric(10, 2), nullable=True)
    saturated_fat_g: float | None = Column(Numeric(10, 2), nullable=True)

    # Provenance — always required
    source_type: NutritionSourceType = Column(
        SQLEnum(NutritionSourceType), nullable=False
    )

    # Relationships
    food_entry: FoodEntry = relationship(
        "FoodEntry", back_populates="nutrition_records"
    )

    def __repr__(self) -> str:
        return f"<NutritionRecord {self.calories}kcal for food_entry={self.food_entry_id}>"

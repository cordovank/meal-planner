"""Profile and ProfileTarget ORM models."""

from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from .base import Base


class Profile(Base):
    """Represents a user profile with nutrition goals."""

    __tablename__ = "profile"
    __allow_unmapped__ = True

    user_id: str | None = Column(String(36), nullable=True, index=True)
    name: str = Column(String(50), nullable=False)
    calorie_target: int | None = Column(Integer, nullable=True)
    calorie_tolerance: int = Column(Integer, nullable=False, default=100)
    is_default: bool = Column(Boolean, nullable=False, default=False)

    # Relationships
    targets = relationship(
        "ProfileTarget",
        back_populates="profile",
        cascade="all, delete-orphan",
        uselist=True,
    )

    def __repr__(self) -> str:
        return f"<Profile {self.name!r} default={self.is_default}>"


class ProfileTarget(Base):
    """Nutrition target for a specific nutrient on a profile."""

    __tablename__ = "profiletarget"
    __allow_unmapped__ = True

    profile_id: str = Column(
        String(36), ForeignKey("profile.id"), nullable=False, index=True
    )
    nutrient_key: str = Column(String(50), nullable=False)
    target_value: float = Column(Numeric(10, 2), nullable=False)
    tolerance_value: float = Column(Numeric(10, 2), nullable=False)
    unit: str = Column(String(20), nullable=False)

    # Relationships
    profile = relationship("Profile", back_populates="targets")

    def __repr__(self) -> str:
        return f"<ProfileTarget {self.nutrient_key}={self.target_value}±{self.tolerance_value}>"

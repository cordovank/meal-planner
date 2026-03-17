"""Recipe repository implementations."""

from __future__ import annotations

from typing import Optional, Protocol
from decimal import Decimal

from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from meal_planner.repository.sqlalchemy.models.recipe import Recipe, RecipeIngredient, RecipeNote


class RecipeRepositoryProtocol(Protocol):
    """Protocol for recipe repository operations."""

    async def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """Get recipe by ID."""
        ...

    async def list_recipes(
        self,
        state: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Recipe], int]:
        """List recipes with optional filtering by state."""
        ...

    async def create(self, recipe: Recipe) -> Recipe:
        """Create a new recipe."""
        ...

    async def update(self, recipe: Recipe) -> Recipe:
        """Update an existing recipe."""
        ...

    async def delete(self, recipe_id: str) -> None:
        """Soft delete a recipe by ID."""
        ...

    async def search(self, query: str, limit: int = 20) -> list[Recipe]:
        """Full-text search recipes by title/description."""
        ...

    async def get_by_title(self, title: str) -> Optional[Recipe]:
        """Get recipe by exact title match."""
        ...

    async def get_ingredients(self, recipe_id: str) -> list[RecipeIngredient]:
        """Get all ingredients for a recipe."""
        ...

    async def add_ingredient(self, ingredient: RecipeIngredient) -> RecipeIngredient:
        """Add an ingredient to a recipe."""
        ...

    async def update_ingredient(self, ingredient: RecipeIngredient) -> RecipeIngredient:
        """Update a recipe ingredient."""
        ...

    async def get_ingredient(self, ingredient_id: str) -> Optional[RecipeIngredient]:
        """Get an ingredient by ID."""
        ...

    async def remove_ingredient(self, ingredient_id: str) -> None:
        """Remove an ingredient from a recipe."""
        ...

    async def get_notes(self, recipe_id: str) -> list[RecipeNote]:
        """Get all notes for a recipe."""
        ...

    async def add_note(self, note: RecipeNote) -> RecipeNote:
        """Add a note to a recipe."""
        ...

    async def get_note(self, note_id: str) -> Optional[RecipeNote]:
        """Get a note by ID."""
        ...

    async def remove_note(self, note_id: str) -> None:
        """Remove a note from a recipe."""
        ...


class SQLAlchemyRecipeRepository:
    """SQLAlchemy implementation of RecipeRepository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    async def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """Get recipe by ID."""
        stmt = select(Recipe).where(
            (Recipe.id == recipe_id) & (Recipe.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_recipes(
        self,
        state: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Recipe], int]:
        """List recipes with optional filtering by state."""
        query = Recipe.deleted_at.is_(None)

        if state:
            query = and_(query, Recipe.state == state)

        count_stmt = select(func.count(Recipe.id)).where(query)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = (
            select(Recipe)
            .where(query)
            .order_by(Recipe.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        recipes = result.scalars().all()

        return recipes, total

    async def create(self, recipe: Recipe) -> Recipe:
        """Create a new recipe."""
        self.session.add(recipe)
        await self.session.flush()
        await self.session.refresh(recipe)
        return recipe

    async def update(self, recipe: Recipe) -> Recipe:
        """Update an existing recipe."""
        await self.session.merge(recipe)
        await self.session.flush()
        # Refresh to get updated timestamps
        updated = await self.get_by_id(recipe.id)
        return updated

    async def delete(self, recipe_id: str) -> None:
        """Soft delete a recipe by ID."""
        recipe = await self.get_by_id(recipe_id)
        if recipe:
            recipe.soft_delete()
            await self.session.flush()

    async def search(self, query: str, limit: int = 20) -> list[Recipe]:
        """Full-text search recipes by title/description using SQLite FTS5.
        
        Note: For Phase 1 with SQLite, we use LIKE pattern matching.
        When migrating to PostgreSQL, this should use full-text search.
        """
        search_pattern = f"%{query}%"
        stmt = (
            select(Recipe)
            .where(
                and_(
                    Recipe.deleted_at.is_(None),
                    or_(
                        Recipe.title.ilike(search_pattern),
                        Recipe.description.ilike(search_pattern),
                    ),
                )
            )
            .order_by(Recipe.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_title(self, title: str) -> Optional[Recipe]:
        """Get recipe by exact title match."""
        stmt = select(Recipe).where(
            (Recipe.title == title) & (Recipe.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_ingredients(self, recipe_id: str) -> list[RecipeIngredient]:
        """Get all ingredients for a recipe."""
        stmt = (
            select(RecipeIngredient)
            .where(RecipeIngredient.recipe_id == recipe_id)
            .order_by(RecipeIngredient.sort_order)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_ingredient(self, ingredient: RecipeIngredient) -> RecipeIngredient:
        """Add an ingredient to a recipe."""
        self.session.add(ingredient)
        await self.session.flush()
        await self.session.refresh(ingredient)
        return ingredient

    async def update_ingredient(self, ingredient: RecipeIngredient) -> RecipeIngredient:
        """Update a recipe ingredient."""
        await self.session.merge(ingredient)
        await self.session.flush()
        updated = await self.session.get(RecipeIngredient, ingredient.id)
        return updated

    async def remove_ingredient(self, ingredient_id: str) -> None:
        """Remove an ingredient from a recipe."""
        ingredient = await self.session.get(RecipeIngredient, ingredient_id)
        if ingredient:
            await self.session.delete(ingredient)
            await self.session.flush()

    async def get_ingredient(self, ingredient_id: str) -> Optional[RecipeIngredient]:
        """Get an ingredient by ID."""
        return await self.session.get(RecipeIngredient, ingredient_id)

    async def get_notes(self, recipe_id: str) -> list[RecipeNote]:
        """Get all notes for a recipe."""
        stmt = select(RecipeNote).where(RecipeNote.recipe_id == recipe_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_note(self, note: RecipeNote) -> RecipeNote:
        """Add a note to a recipe."""
        self.session.add(note)
        await self.session.flush()
        await self.session.refresh(note)
        return note

    async def remove_note(self, note_id: str) -> None:
        """Remove a note from a recipe."""
        note = await self.session.get(RecipeNote, note_id)
        if note:
            await self.session.delete(note)
            await self.session.flush()

    async def get_note(self, note_id: str) -> Optional[RecipeNote]:
        """Get a note by ID."""
        return await self.session.get(RecipeNote, note_id)



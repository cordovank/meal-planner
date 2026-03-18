"""Recipe service with business logic."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from meal_planner.repository.sqlalchemy.models.recipe import Recipe, RecipeIngredient, RecipeNote, RecipeState
from meal_planner.repository.sqlalchemy.repositories.recipe_repository import RecipeRepositoryProtocol


class RecipeService:
    """Service for recipe operations."""

    def __init__(self, recipe_repo: RecipeRepositoryProtocol):
        """Initialize service with repository."""
        self.recipe_repo = recipe_repo

    async def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """Get a recipe by ID."""
        return await self.recipe_repo.get_by_id(recipe_id)

    async def list_recipes(
        self,
        state: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Recipe], int]:
        """List recipes with optional filtering."""
        return await self.recipe_repo.list_recipes(state=state, limit=limit, offset=offset)

    async def create_recipe(
        self,
        title: str,
        state: str = RecipeState.DRAFT,
        base_servings: int = 1,
        description: Optional[str] = None,
        prep_time_minutes: Optional[int] = None,
        cook_time_minutes: Optional[int] = None,
        user_id: Optional[str] = None,
    ) -> Recipe:
        """Create a new recipe."""
        recipe = Recipe(
            id=str(uuid.uuid4()),
            title=title,
            state=state,
            base_servings=base_servings,
            description=description,
            prep_time_minutes=prep_time_minutes,
            cook_time_minutes=cook_time_minutes,
            user_id=user_id,
        )
        return await self.recipe_repo.create(recipe)

    async def update_recipe(
        self,
        recipe_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        state: Optional[str] = None,
        base_servings: Optional[int] = None,
        prep_time_minutes: Optional[int] = None,
        cook_time_minutes: Optional[int] = None,
    ) -> Optional[Recipe]:
        """Update recipe fields."""
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            return None

        if title is not None:
            recipe.title = title
        if description is not None:
            recipe.description = description
        if state is not None:
            recipe.state = state
        if base_servings is not None:
            recipe.base_servings = base_servings
        if prep_time_minutes is not None:
            recipe.prep_time_minutes = prep_time_minutes
        if cook_time_minutes is not None:
            recipe.cook_time_minutes = cook_time_minutes

        return await self.recipe_repo.update(recipe)

    async def delete_recipe(self, recipe_id: str) -> bool:
        """Soft delete a recipe."""
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            return False

        await self.recipe_repo.delete(recipe_id)
        return True

    async def add_ingredient(
        self,
        recipe_id: str,
        name: str,
        amount: Optional[Decimal] = None,
        unit: Optional[str] = None,
        food_entry_id: Optional[str] = None,
        to_taste: bool = False,
        optional: bool = False,
        notes: Optional[str] = None,
    ) -> Optional[RecipeIngredient]:
        """Add an ingredient to a recipe."""
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            return None

        # Get next sort order
        ingredients = await self.recipe_repo.get_ingredients(recipe_id)
        sort_order = max([ing.sort_order for ing in ingredients], default=-1) + 1

        ingredient = RecipeIngredient(
            id=str(uuid.uuid4()),
            recipe_id=recipe_id,
            name=name,
            amount=amount,
            unit=unit,
            food_entry_id=food_entry_id,
            to_taste=to_taste,
            optional=optional,
            notes=notes,
            sort_order=sort_order,
        )

        return await self.recipe_repo.add_ingredient(ingredient)

    async def update_ingredient(
        self,
        ingredient_id: str,
        name: Optional[str] = None,
        amount: Optional[Decimal] = None,
        unit: Optional[str] = None,
        food_entry_id: Optional[str] = None,
        to_taste: Optional[bool] = None,
        optional: Optional[bool] = None,
        notes: Optional[str] = None,
    ) -> Optional[RecipeIngredient]:
        """Update a recipe ingredient."""
        ingredient = await self.recipe_repo.get_ingredient(ingredient_id)
        if not ingredient:
            return None

        if name is not None:
            ingredient.name = name
        if amount is not None:
            ingredient.amount = amount
        if unit is not None:
            ingredient.unit = unit
        if food_entry_id is not None:
            ingredient.food_entry_id = food_entry_id
        if to_taste is not None:
            ingredient.to_taste = to_taste
        if optional is not None:
            ingredient.optional = optional
        if notes is not None:
            ingredient.notes = notes

        return await self.recipe_repo.update_ingredient(ingredient)

    async def remove_ingredient(self, ingredient_id: str) -> bool:
        """Remove an ingredient from a recipe."""
        ingredient = await self.recipe_repo.get_ingredient(ingredient_id)
        if not ingredient:
            return False

        await self.recipe_repo.remove_ingredient(ingredient_id)
        return True

    async def add_note(self, recipe_id: str, text: str) -> Optional[RecipeNote]:
        """Add a note to a recipe."""
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            return None

        note = RecipeNote(
            id=str(uuid.uuid4()),
            recipe_id=recipe_id,
            text=text,
        )

        return await self.recipe_repo.add_note(note)

    async def remove_note(self, note_id: str) -> bool:
        """Remove a note from a recipe."""
        note = await self.recipe_repo.get_note(note_id)
        if not note:
            return False

        await self.recipe_repo.remove_note(note_id)
        return True

    async def duplicate_recipe(
        self,
        recipe_id: str,
        new_title: str,
        version_label: Optional[str] = None,
    ) -> Optional[Recipe]:
        """Duplicate a recipe with optional version label."""
        original = await self.recipe_repo.get_by_id(recipe_id)
        if not original:
            return None

        new_recipe = Recipe(
            id=str(uuid.uuid4()),
            user_id=original.user_id,
            title=new_title,
            description=original.description,
            state=RecipeState.DRAFT,
            base_servings=original.base_servings,
            prep_time_minutes=original.prep_time_minutes,
            cook_time_minutes=original.cook_time_minutes,
            parent_recipe_id=recipe_id,
            version_label=version_label,
        )

        created = await self.recipe_repo.create(new_recipe)

        # Copy ingredients
        original_ingredients = await self.recipe_repo.get_ingredients(recipe_id)
        for orig_ing in original_ingredients:
            await self.recipe_repo.add_ingredient(
                RecipeIngredient(
                    id=str(uuid.uuid4()),
                    recipe_id=created.id,
                    food_entry_id=orig_ing.food_entry_id,
                    name=orig_ing.name,
                    amount=orig_ing.amount,
                    unit=orig_ing.unit,
                    to_taste=orig_ing.to_taste,
                    optional=orig_ing.optional,
                    notes=orig_ing.notes,
                    sort_order=orig_ing.sort_order,
                )
            )

        return created

    async def search_recipes(self, query: str, limit: int = 20) -> list[Recipe]:
        """Search recipes by title/description."""
        return await self.recipe_repo.search(query, limit=limit)

    def scale_recipe(
        self,
        recipe: Recipe,
        new_servings: int,
        ingredients: list | None = None,
    ) -> dict[str, any]:
        """Calculate scaled ingredients for a recipe.

        Returns a dict with scaling factor and scaled ingredients.
        This is a synchronous calculation method.

        Args:
            recipe: The recipe to scale.
            new_servings: Target number of servings.
            ingredients: Pre-loaded ingredient list. If None, falls back to
                recipe.ingredients (requires eagerly loaded relationship).
        """
        if recipe.base_servings == 0:
            return {"factor": 1.0, "ingredients": []}

        factor = Decimal(new_servings) / Decimal(recipe.base_servings)

        ingredient_list = ingredients if ingredients is not None else recipe.ingredients
        scaled_ingredients = []
        for ing in ingredient_list:
            scaled_ing = {
                "id": ing.id,
                "name": ing.name,
                "amount": ing.amount * factor if ing.amount else None,
                "unit": ing.unit,
                "to_taste": ing.to_taste,
                "optional": ing.optional,
            }
            scaled_ingredients.append(scaled_ing)

        return {
            "factor": float(factor),
            "ingredients": scaled_ingredients,
            "servings": new_servings,
        }

    async def get_recipe_with_relations(self, recipe_id: str) -> Optional[dict]:
        """Get recipe with all relations loaded for API responses."""
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            return None

        ingredients = await self.recipe_repo.get_ingredients(recipe_id)
        notes = await self.recipe_repo.get_notes(recipe_id)

        return {
            "recipe": recipe,
            "ingredients": ingredients,
            "notes": notes,
        }

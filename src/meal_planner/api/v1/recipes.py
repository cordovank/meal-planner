"""Recipe API endpoints."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from meal_planner.api.schemas.recipe import (
    RecipeCreateSchema,
    RecipeDetailSchema,
    RecipeDuplicateRequestSchema,
    RecipeIngredientCreateSchema,
    RecipeListResponseSchema,
    RecipeNoteCreateSchema,
    RecipeScaleRequestSchema,
    RecipeScaleResponseSchema,
    RecipeUpdateSchema,
)
from meal_planner.api.schemas.recipe import RecipeNutritionBreakdownSchema
from meal_planner.repository.sqlalchemy.models.recipe import RecipeIngredient, RecipeNote
from meal_planner.repository.sqlalchemy.repositories.food_repository import SQLAlchemyFoodRepository
from meal_planner.repository.sqlalchemy.repositories.recipe_repository import SQLAlchemyRecipeRepository
from meal_planner.repository.sqlalchemy.session import get_session
from meal_planner.services.recipe_service import RecipeService

router = APIRouter(tags=["recipes"])


async def get_recipe_service(session: AsyncSession = Depends(get_session)) -> RecipeService:
    """Dependency for recipe service."""
    recipe_repo = SQLAlchemyRecipeRepository(session)
    food_repo = SQLAlchemyFoodRepository(session)
    return RecipeService(recipe_repo, food_repo=food_repo)


@router.get("/api/v1/recipes", response_model=RecipeListResponseSchema)
async def list_recipes(
    state: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None),
    service: RecipeService = Depends(get_recipe_service),
) -> RecipeListResponseSchema:
    """List recipes with optional filtering and search."""
    
    if q:
        # Search mode
        items = await service.search_recipes(q, limit=limit)
        return RecipeListResponseSchema(
            items=[
                {
                    "id": recipe.id,
                    "title": recipe.title,
                    "state": recipe.state,
                    "base_servings": recipe.base_servings,
                    "prep_time_minutes": recipe.prep_time_minutes,
                    "cook_time_minutes": recipe.cook_time_minutes,
                    "created_at": recipe.created_at,
                    "updated_at": recipe.updated_at,
                    "deleted_at": recipe.deleted_at,
                }
                for recipe in items
            ],
            total=len(items),
            has_more=len(items) >= limit,
        )
    else:
        # List mode with optional state filter
        items, total = await service.list_recipes(state=state, limit=limit, offset=offset)
        return RecipeListResponseSchema(
            items=[
                {
                    "id": recipe.id,
                    "title": recipe.title,
                    "state": recipe.state,
                    "base_servings": recipe.base_servings,
                    "prep_time_minutes": recipe.prep_time_minutes,
                    "cook_time_minutes": recipe.cook_time_minutes,
                    "created_at": recipe.created_at,
                    "updated_at": recipe.updated_at,
                    "deleted_at": recipe.deleted_at,
                }
                for recipe in items
            ],
            total=total,
            has_more=(offset + limit) < total,
        )


@router.post("/api/v1/recipes", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    data: RecipeCreateSchema,
    service: RecipeService = Depends(get_recipe_service),
) -> dict:
    """Create a new recipe."""
    recipe = await service.create_recipe(
        title=data.title,
        state=data.state,
        base_servings=data.base_servings,
        description=data.description,
        prep_time_minutes=data.prep_time_minutes,
        cook_time_minutes=data.cook_time_minutes,
    )

    # Add ingredients if provided
    for ing in data.ingredients:
        await service.add_ingredient(
            recipe_id=recipe.id,
            name=ing.name,
            amount=ing.amount,
            unit=ing.unit,
            food_entry_id=str(ing.food_entry_id) if ing.food_entry_id else None,
            to_taste=ing.to_taste,
            optional=ing.optional,
            notes=ing.notes,
        )

    return {
        "id": recipe.id,
        "title": recipe.title,
        "state": recipe.state,
        "created_at": recipe.created_at,
    }


@router.get("/api/v1/recipes/{recipe_id}", response_model=RecipeDetailSchema)
async def get_recipe(
    recipe_id: str,
    service: RecipeService = Depends(get_recipe_service),
) -> RecipeDetailSchema:
    """Get recipe details with nutrition and notes."""
    recipe = await service.get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    relations = await service.get_recipe_with_relations(recipe_id)

    return RecipeDetailSchema(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        state=recipe.state,
        base_servings=recipe.base_servings,
        prep_time_minutes=recipe.prep_time_minutes,
        cook_time_minutes=recipe.cook_time_minutes,
        ingredients=[
            {
                "id": ing.id,
                "name": ing.name,
                "amount": ing.amount,
                "unit": ing.unit,
                "food_entry_id": ing.food_entry_id,
                "to_taste": ing.to_taste,
                "optional": ing.optional,
                "notes": ing.notes,
                "sort_order": ing.sort_order,
            }
            for ing in (relations["ingredients"] if relations else [])
        ],
        notes=[
            {
                "id": note.id,
                "text": note.text,
                "created_at": note.created_at,
            }
            for note in (relations["notes"] if relations else [])
        ],
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
        deleted_at=recipe.deleted_at,
    )


@router.put("/api/v1/recipes/{recipe_id}", response_model=RecipeDetailSchema)
async def update_recipe(
    recipe_id: str,
    data: RecipeUpdateSchema,
    service: RecipeService = Depends(get_recipe_service),
) -> RecipeDetailSchema:
    """Update recipe details."""
    recipe = await service.update_recipe(
        recipe_id,
        title=data.title,
        description=data.description,
        state=data.state,
        base_servings=data.base_servings,
        prep_time_minutes=data.prep_time_minutes,
        cook_time_minutes=data.cook_time_minutes,
    )

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    relations = await service.get_recipe_with_relations(recipe_id)

    return RecipeDetailSchema(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        state=recipe.state,
        base_servings=recipe.base_servings,
        prep_time_minutes=recipe.prep_time_minutes,
        cook_time_minutes=recipe.cook_time_minutes,
        ingredients=[
            {
                "id": ing.id,
                "name": ing.name,
                "amount": ing.amount,
                "unit": ing.unit,
                "food_entry_id": ing.food_entry_id,
                "to_taste": ing.to_taste,
                "optional": ing.optional,
                "notes": ing.notes,
                "sort_order": ing.sort_order,
            }
            for ing in (relations["ingredients"] if relations else [])
        ],
        notes=[
            {
                "id": note.id,
                "text": note.text,
                "created_at": note.created_at,
            }
            for note in (relations["notes"] if relations else [])
        ],
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
        deleted_at=recipe.deleted_at,
    )


@router.delete("/api/v1/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: str,
    service: RecipeService = Depends(get_recipe_service),
) -> None:
    """Soft delete a recipe."""
    success = await service.delete_recipe(recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")


@router.post("/api/v1/recipes/{recipe_id}/scale", response_model=RecipeScaleResponseSchema)
async def scale_recipe(
    recipe_id: str,
    data: RecipeScaleRequestSchema,
    service: RecipeService = Depends(get_recipe_service),
) -> RecipeScaleResponseSchema:
    """Scale recipe to new serving count."""
    recipe = await service.get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    relations = await service.get_recipe_with_relations(recipe_id)
    scale_result = service.scale_recipe(
        recipe, data.new_servings, ingredients=relations["ingredients"]
    )

    return RecipeScaleResponseSchema(
        factor=scale_result["factor"],
        servings=scale_result["servings"],
        ingredients=scale_result["ingredients"],
    )


@router.post("/api/v1/recipes/{recipe_id}/duplicate", status_code=status.HTTP_201_CREATED)
async def duplicate_recipe(
    recipe_id: str,
    data: RecipeDuplicateRequestSchema,
    service: RecipeService = Depends(get_recipe_service),
) -> dict:
    """Duplicate recipe, optionally as version."""
    new_recipe = await service.duplicate_recipe(
        recipe_id=recipe_id,
        new_title=data.title,
        version_label=data.version_label,
    )

    if not new_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {
        "id": new_recipe.id,
        "title": new_recipe.title,
        "state": new_recipe.state,
        "parent_recipe_id": new_recipe.parent_recipe_id,
        "version_label": new_recipe.version_label,
        "created_at": new_recipe.created_at,
    }


@router.post("/api/v1/recipes/{recipe_id}/ingredients", status_code=status.HTTP_201_CREATED)
async def add_ingredient(
    recipe_id: str,
    data: RecipeIngredientCreateSchema,
    service: RecipeService = Depends(get_recipe_service),
) -> dict:
    """Add an ingredient to a recipe."""
    ingredient = await service.add_ingredient(
        recipe_id=recipe_id,
        name=data.name,
        amount=data.amount,
        unit=data.unit,
        food_entry_id=str(data.food_entry_id) if data.food_entry_id else None,
        to_taste=data.to_taste,
        optional=data.optional,
        notes=data.notes,
    )

    if not ingredient:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {
        "id": ingredient.id,
        "name": ingredient.name,
        "amount": ingredient.amount,
        "unit": ingredient.unit,
    }


@router.put("/api/v1/recipes/ingredients/{ingredient_id}")
async def update_ingredient(
    ingredient_id: str,
    data: RecipeIngredientCreateSchema,
    service: RecipeService = Depends(get_recipe_service),
) -> dict:
    """Update a recipe ingredient."""
    ingredient = await service.update_ingredient(
        ingredient_id=ingredient_id,
        name=data.name,
        amount=data.amount,
        unit=data.unit,
        food_entry_id=str(data.food_entry_id) if data.food_entry_id else None,
        to_taste=data.to_taste,
        optional=data.optional,
        notes=data.notes,
    )

    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    return {
        "id": ingredient.id,
        "name": ingredient.name,
        "amount": ingredient.amount,
        "unit": ingredient.unit,
    }


@router.delete("/api/v1/recipes/ingredients/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_ingredient(
    ingredient_id: str,
    service: RecipeService = Depends(get_recipe_service),
) -> None:
    """Remove an ingredient from a recipe."""
    success = await service.remove_ingredient(ingredient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ingredient not found")


@router.post("/api/v1/recipes/{recipe_id}/notes", status_code=status.HTTP_201_CREATED)
async def add_note(
    recipe_id: str,
    data: RecipeNoteCreateSchema,
    service: RecipeService = Depends(get_recipe_service),
) -> dict:
    """Add a note to a recipe."""
    note = await service.add_note(recipe_id=recipe_id, text=data.text)

    if not note:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {
        "id": note.id,
        "text": note.text,
        "created_at": note.created_at,
    }


@router.delete("/api/v1/recipes/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_note(
    note_id: str,
    service: RecipeService = Depends(get_recipe_service),
) -> None:
    """Remove a note from a recipe."""
    success = await service.remove_note(note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")


@router.get("/api/v1/recipes/{recipe_id}/nutrition", response_model=RecipeNutritionBreakdownSchema)
async def get_recipe_nutrition(
    recipe_id: str,
    service: RecipeService = Depends(get_recipe_service),
) -> RecipeNutritionBreakdownSchema:
    """Get detailed nutrition breakdown for a recipe."""
    result = await service.get_recipe_nutrition(recipe_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return RecipeNutritionBreakdownSchema(
        total=result["total"],
        per_serving=result["per_serving"],
        by_ingredient=result["by_ingredient"],
        confidence_overall=result["confidence_overall"],
        characterization=result.get("characterization", []),
        missing_data=result["missing_data"],
    )

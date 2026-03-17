"""
Integration tests for recipe service functionality.
Tests cover critical paths: CRUD operations, scaling, duplication.
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from meal_planner.repository.sqlalchemy.session import get_sessionmaker
from meal_planner.services.recipe_service import RecipeService
from meal_planner.api.schemas.recipe import (
    RecipeCreateSchema,
    RecipeIngredientCreateSchema,
    RecipeScaleRequestSchema,
    RecipeDuplicateRequestSchema
)
# Import models to ensure mappers are registered
from meal_planner.repository.sqlalchemy.models.recipe import Recipe, RecipeIngredient, RecipeNote


@pytest.fixture
async def db_session():
    """Provide a database session for tests."""
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        yield session


@pytest.fixture
async def recipe_service(db_session: AsyncSession):
    """Provide a recipe service instance."""
    from meal_planner.repository.sqlalchemy.repositories.recipe_repository import SQLAlchemyRecipeRepository
    repo = SQLAlchemyRecipeRepository(db_session)
    return RecipeService(repo)


@pytest.mark.asyncio
async def test_create_recipe(recipe_service: RecipeService):
    """Test creating a new recipe with ingredients."""
    recipe = await recipe_service.create_recipe(
        title="Test Recipe",
        description="A test recipe",
        base_servings=4,
        prep_time_minutes=30,
        cook_time_minutes=45,
    )

    # Add ingredients
    await recipe_service.add_ingredient(
        recipe_id=recipe.id,
        name="Flour",
        amount=2.0,
        unit="cups",
        notes="All-purpose"
    )
    await recipe_service.add_ingredient(
        recipe_id=recipe.id,
        name="Eggs",
        amount=3,
        unit="pieces"
    )

    # Retrieve to verify
    relations = await recipe_service.get_recipe_with_relations(recipe.id)

    assert relations is not None
    assert relations["recipe"].title == "Test Recipe"
    assert relations["recipe"].base_servings == 4
    assert len(relations["ingredients"]) == 2
    assert relations["ingredients"][0].name == "Flour"
    assert relations["ingredients"][1].name == "Eggs"


@pytest.mark.asyncio
async def test_get_recipe(recipe_service: RecipeService):
    """Test retrieving a recipe by ID."""
    # First create a recipe
    recipe = await recipe_service.create_recipe(
        title="Get Test Recipe",
        description="For retrieval test",
        base_servings=2
    )
    await recipe_service.add_ingredient(
        recipe_id=recipe.id,
        name="Sugar",
        amount=1.0,
        unit="cup"
    )

    # Now retrieve it
    retrieved = await recipe_service.get_recipe(recipe.id)

    assert retrieved.id == recipe.id
    assert retrieved.title == "Get Test Recipe"


@pytest.mark.asyncio
async def test_update_recipe(recipe_service: RecipeService):
    """Test updating recipe details."""
    # Create recipe
    recipe = await recipe_service.create_recipe(
        title="Update Test",
        description="Before update",
        base_servings=2
    )
    await recipe_service.add_ingredient(
        recipe_id=recipe.id,
        name="Milk",
        amount=1.0,
        unit="cup"
    )

    # Update it
    updated = await recipe_service.update_recipe(
        recipe_id=recipe.id,
        title="Updated Test",
        description="After update",
        base_servings=4
    )

    assert updated.title == "Updated Test"
    assert updated.base_servings == 4


@pytest.mark.asyncio
async def test_delete_recipe(recipe_service: RecipeService):
    """Test soft deleting a recipe."""
    # Create recipe
    recipe = await recipe_service.create_recipe(
        title="Delete Test",
        base_servings=1
    )

    # Delete it
    result = await recipe_service.delete_recipe(recipe.id)
    assert result is True

    # Try to retrieve - should be None
    retrieved = await recipe_service.get_recipe(recipe.id)
    assert retrieved is None  # Assuming soft delete hides it


@pytest.mark.asyncio
async def test_scale_recipe(recipe_service: RecipeService):
    """Test scaling recipe ingredients."""
    # Create recipe
    recipe = await recipe_service.create_recipe(
        title="Scale Test",
        base_servings=2
    )
    await recipe_service.add_ingredient(
        recipe_id=recipe.id,
        name="Butter",
        amount=4.0,
        unit="tbsp"
    )
    await recipe_service.add_ingredient(
        recipe_id=recipe.id,
        name="Flour",
        amount=1.0,
        unit="cup"
    )

    # Get recipe with relations for scaling
    relations = await recipe_service.get_recipe_with_relations(recipe.id)
    
    # Create a simple object for scaling
    class MockRecipe:
        def __init__(self, base_servings, ingredients):
            self.base_servings = base_servings
            self.ingredients = ingredients

    mock_recipe = MockRecipe(recipe.base_servings, relations["ingredients"])

    # Scale to 4 servings
    scaled = recipe_service.scale_recipe(mock_recipe, 4)

    assert scaled["servings"] == 4
    assert len(scaled["ingredients"]) == 2
    # Assuming linear scaling
    assert scaled["ingredients"][0]["amount"] == 8.0  # 4 * 2
    assert scaled["ingredients"][1]["amount"] == 2.0  # 1 * 2


@pytest.mark.asyncio
async def test_duplicate_recipe(recipe_service: RecipeService):
    """Test duplicating a recipe."""
    # Create original recipe
    original = await recipe_service.create_recipe(
        title="Original Recipe",
        description="To be duplicated",
        base_servings=3
    )
    await recipe_service.add_ingredient(
        recipe_id=original.id,
        name="Salt",
        amount=0.5,
        unit="tsp"
    )

    # Duplicate it
    duplicated = await recipe_service.duplicate_recipe(
        recipe_id=original.id,
        new_title="Duplicated Recipe"
    )

    assert duplicated.id != original.id
    assert duplicated.title == "Duplicated Recipe"
    assert duplicated.base_servings == 3

    # Check ingredients were copied
    dup_relations = await recipe_service.get_recipe_with_relations(duplicated.id)
    assert len(dup_relations["ingredients"]) == 1
    assert dup_relations["ingredients"][0].name == "Salt"


@pytest.mark.asyncio
async def test_list_recipes(recipe_service: RecipeService):
    """Test listing recipes with search."""
    # Create a few recipes
    await recipe_service.create_recipe(title="Pasta Recipe", base_servings=4)
    await recipe_service.create_recipe(title="Salad Recipe", base_servings=2)
    await recipe_service.create_recipe(title="Soup Recipe", base_servings=6)

    # List all
    recipes, total = await recipe_service.list_recipes()
    assert total >= 3

    # Search for "Recipe"
    search_results = await recipe_service.search_recipes("Recipe")
    assert len(search_results) >= 3
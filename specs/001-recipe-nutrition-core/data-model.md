# Data Model: Recipe Home & Nutrition-Aware Meal Planner — Phase 1 MVP

**Date**: 2026-03-16 | **Context**: Phase 1 MVP entities and relationships

## Overview

The data model supports recipe management, nutrition calculation, user profiles, meal planning, daily logging, and gap detection. All entities use UUID primary keys, audit timestamps, and soft deletes for cloud migration compatibility.

## Core Entities

### Recipe
Represents a homemade recipe with structured or draft content.

**Fields**:
- `id`: UUID (PK)
- `user_id`: UUID (FK to User, nullable for Phase 1 single-user)
- `title`: String (required, max 200)
- `description`: Text (optional)
- `state`: Enum (draft, pending_review, incomplete, finalized)
- `base_servings`: Integer (required, min 1)
- `prep_time_minutes`: Integer (optional)
- `cook_time_minutes`: Integer (optional)
- `parent_recipe_id`: UUID (FK to Recipe, nullable for versioning)
- `version_label`: String (optional, e.g., "low-sodium")
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (nullable)

**Relationships**:
- 1:N RecipeIngredient
- 1:N RecipeNote
- N:M RecipeCollection (via junction table)
- 1:N LeftoverBatch

**Validation Rules**:
- Title required for all states
- State transitions: draft → any, but finalized requires complete ingredients
- Versioning: parent_recipe_id creates lineage

### RecipeIngredient
Links ingredients to recipes with amounts and nutrition.

**Fields**:
- `id`: UUID (PK)
- `recipe_id`: UUID (FK to Recipe)
- `food_entry_id`: UUID (FK to FoodEntry, nullable)
- `name`: String (required, max 100)
- `amount`: Decimal (nullable, min 0)
- `unit`: String (nullable, e.g., "g", "cup")
- `to_taste`: Boolean (default false)
- `optional`: Boolean (default false)
- `notes`: Text (optional)
- `sort_order`: Integer (for ordering)

**Relationships**:
- N:1 Recipe
- N:1 FoodEntry

**Validation Rules**:
- Either food_entry_id or manual nutrition required
- Amount/unit consistency (e.g., no unit without amount)

### FoodEntry
Represents a food item in the local ingredient library.

**Fields**:
- `id`: UUID (PK)
- `user_id`: UUID (FK, nullable for system entries)
- `name`: String (required, max 200)
- `brand`: String (optional)
- `category`: String (optional)
- `source_type`: Enum (usda, open_food_facts, barcode, user_created, calculated)
- `source_id`: String (optional, external ID)
- `is_custom`: Boolean (default false)
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (nullable)

**Relationships**:
- 1:N NutritionRecord
- 1:N RecipeIngredient

**Validation Rules**:
- System entries (USDA/OFF) have source_id
- Custom entries marked is_custom=true

### NutritionRecord
Contains nutrition data for a FoodEntry.

**Fields**:
- `id`: UUID (PK)
- `food_entry_id`: UUID (FK to FoodEntry)
- `serving_size`: Decimal (required, min 0)
- `serving_unit`: String (required, e.g., "g", "cup")
- `calories`: Decimal (required, min 0)
- `protein_g`: Decimal (required, min 0)
- `carbohydrates_g`: Decimal (required, min 0)
- `fat_g`: Decimal (required, min 0)
- `fiber_g`: Decimal (optional, min 0)
- `total_sugar_g`: Decimal (optional, min 0)
- `added_sugar_g`: Decimal (required, min 0)  // First-class field
- `sodium_mg`: Decimal (optional, min 0)
- `saturated_fat_g`: Decimal (optional, min 0)
- `source_type`: Enum (label, barcode, user_confirmed, estimated, calculated)  // Non-null
- `created_at`: DateTime
- `updated_at`: DateTime

**Relationships**:
- N:1 FoodEntry

**Validation Rules**:
- source_type always populated
- added_sugar_g treated as first-class (never optional in logic)

### Profile
Represents a user's nutrition goals and preferences.

**Fields**:
- `id`: UUID (PK)
- `user_id`: UUID (FK, nullable Phase 1)
- `name`: String (required, max 50)
- `calorie_target`: Integer (optional)
- `calorie_tolerance`: Integer (default 100)
- `is_default`: Boolean (default false)
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (nullable)

**Relationships**:
- 1:N ProfileTarget
- 1:N LogEntry

**Validation Rules**:
- At least one target defined (calories or macros)
- Tolerance ranges prevent negative values

### ProfileTarget
Per-nutrient target with tolerance.

**Fields**:
- `id`: UUID (PK)
- `profile_id`: UUID (FK to Profile)
- `nutrient_key`: Enum (calories, protein_g, carbohydrates_g, fat_g, added_sugar_g, etc.)
- `target_value`: Decimal (required, min 0)
- `tolerance_value`: Decimal (required, min 0)  // ± absolute
- `unit`: String (required, e.g., "kcal", "g")

**Relationships**:
- N:1 Profile

**Validation Rules**:
- nutrient_key matches valid nutrients
- tolerance_value < target_value to prevent impossible ranges

### LogEntry
Represents a logged meal on a specific day.

**Fields**:
- `id`: UUID (PK)
- `user_id`: UUID (FK, nullable Phase 1)
- `profile_id`: UUID (FK to Profile)
- `date`: Date (required)
- `meal_slot`: Enum (breakfast, lunch, dinner, snack, custom)
- `recipe_id`: UUID (FK to Recipe, nullable)
- `portion_size`: Decimal (default 1.0, min 0)
- `notes`: Text (optional)
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (nullable)

**Relationships**:
- N:1 Profile
- N:1 Recipe

**Validation Rules**:
- Date not in future
- Portion size affects nutrition scaling

### LeftoverBatch
Tracks prepared batches with remaining servings.

**Fields**:
- `id`: UUID (PK)
- `recipe_id`: UUID (FK to Recipe)
- `initial_servings`: Integer (required, min 1)
- `servings_remaining`: Integer (required, min 0)
- `prepared_date`: Date (required)
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (nullable)

**Relationships**:
- N:1 Recipe

**Validation Rules**:
- servings_remaining <= initial_servings
- Soft delete when servings_remaining = 0

### MealTemplate
Reusable meal combination for quick logging.

**Fields**:
- `id`: UUID (PK)
- `user_id`: UUID (FK, nullable Phase 1)
- `name`: String (required, max 100)
- `meal_slot`: Enum (breakfast, lunch, dinner, snack, custom)
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (nullable)

**Relationships**:
- 1:N MealTemplateItem (junction to Recipe with portion)

**Validation Rules**:
- At least one item required

### RecipeNote
Timestamped notes attached to recipes.

**Fields**:
- `id`: UUID (PK)
- `recipe_id`: UUID (FK to Recipe)
- `note_text`: Text (required)
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (nullable)

**Relationships**:
- N:1 Recipe

**Validation Rules**:
- Note text non-empty

## Relationships Overview

```
Recipe 1:N RecipeIngredient N:1 FoodEntry
Recipe 1:N RecipeNote
Recipe 1:N LeftoverBatch
Recipe N:M RecipeCollection (junction)

FoodEntry 1:N NutritionRecord
FoodEntry 1:N RecipeIngredient

Profile 1:N ProfileTarget
Profile 1:N LogEntry

LogEntry N:1 Recipe (optional)
LogEntry N:1 Profile

MealTemplate 1:N MealTemplateItem N:1 Recipe
```

## State Transitions

### Recipe States
- `draft` → `incomplete` | `pending_review` | `finalized`
- `incomplete` → `pending_review` | `finalized`
- `pending_review` → `incomplete` | `finalized`
- `finalized` → `pending_review` (for edits)

### Leftover Batch Lifecycle
- Created with initial_servings > 0
- servings_remaining decremented on consumption
- Soft deleted when servings_remaining = 0

## Data Integrity Rules

- All FKs cascade soft delete (set deleted_at on parent)
- Nutrition calculations never modify stored data
- Audit timestamps updated on all changes
- UUIDs prevent ID collision in future multi-user

## Migration Path Notes

- Schema compatible with PostgreSQL (UUID, JSON for complex fields if needed)
- Soft deletes enable audit trails
- No auto-increment IDs to avoid migration complexity
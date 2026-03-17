# Tasks: Recipe Home & Nutrition-Aware Meal Planner — Phase 1 MVP

**Input**: Design documents from `/specs/001-recipe-nutrition-core/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - not requested in specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/meal_planner/`, `tests/` at repository root
- Paths based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create initial Alembic migration for base schema in src/meal_planner/repository/migrations/versions/
- [X] T002 [P] Configure Pydantic schemas for common types in src/meal_planner/api/schemas/common.py
- [X] T003 [P] Setup basic error handling middleware in src/meal_planner/api/middleware.py
- [X] T004 [P] Initialize Jinja2 templates structure in src/meal_planner/web/templates/
- [X] T005 [P] Configure static file serving in src/meal_planner/web/static/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create base entity models with UUID PKs and audit fields in src/meal_planner/repository/sqlalchemy/models/base.py
- [X] T007 [P] Implement repository protocol interfaces in src/meal_planner/services/interfaces.py
- [X] T008 [P] Setup SQLAlchemy async session management in src/meal_planner/repository/sqlalchemy/session.py
- [X] T009 [P] Create unit conversion utility functions in src/meal_planner/services/unit_conversion.py
- [X] T010 [P] Implement fuzzy search utility using RapidFuzz in src/meal_planner/infra/search/fuzzy.py
- [X] T011 [P] Setup nutrition calculation service foundation in src/meal_planner/services/nutrition_calculator.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Preserve and Organize Homemade Recipes (Priority: P1) 🎯 MVP

**Goal**: Allow users to create, store, edit, search, and organize homemade recipes in various states of completion.

**Independent Test**: Create a recipe with ingredients and instructions, save it, retrieve it in list view, edit it, and delete it. Verify draft recipes can be saved without full data.

### Implementation for User Story 1

- [ ] T012 [P] [US1] Create Recipe and RecipeIngredient models in src/meal_planner/repository/sqlalchemy/models/recipe.py
- [ ] T013 [P] [US1] Create RecipeNote model in src/meal_planner/repository/sqlalchemy/models/recipe_note.py
- [ ] T014 [P] [US1] Implement RecipeRepository protocol in src/meal_planner/repository/sqlalchemy/repositories/recipe_repository.py
- [ ] T015 [US1] Create RecipeService with CRUD operations in src/meal_planner/services/recipe_service.py
- [ ] T016 [P] [US1] Create Pydantic schemas for recipe API in src/meal_planner/api/schemas/recipe.py
- [ ] T017 [US1] Implement recipe API endpoints in src/meal_planner/api/v1/recipes.py
- [ ] T018 [P] [US1] Add recipe scaling logic to RecipeService
- [ ] T019 [P] [US1] Implement recipe duplication/versioning in RecipeService
- [ ] T020 [P] [US1] Add full-text search for recipes using FTS5 in RecipeRepository
- [ ] T021 [P] [US1] Create recipe list template in src/meal_planner/web/templates/recipes/list.html
- [ ] T022 [P] [US1] Create recipe detail template in src/meal_planner/web/templates/recipes/detail.html
- [ ] T023 [P] [US1] Create recipe form template in src/meal_planner/web/templates/recipes/form.html

**Checkpoint**: User Story 1 fully functional - recipes can be created, edited, searched, and organized

---

## Phase 4: User Story 2 - Understand Recipe and Meal Nutrition with Confidence (Priority: P1)

**Goal**: Display nutrition information for recipes with confidence indicators and automatic characterization labels.

**Independent Test**: Link ingredients to nutrition data, view recipe nutrition summary with confidence levels, see characterization labels.

### Implementation for User Story 2

- [ ] T024 [P] [US2] Create FoodEntry and NutritionRecord models in src/meal_planner/repository/sqlalchemy/models/food.py
- [ ] T025 [P] [US2] Implement FoodRepository protocol in src/meal_planner/repository/sqlalchemy/repositories/food_repository.py
- [ ] T026 [US2] Extend RecipeService with nutrition calculation methods
- [ ] T027 [P] [US2] Create Pydantic schemas for food/nutrition API in src/meal_planner/api/schemas/food.py
- [ ] T028 [US2] Implement food library API endpoints in src/meal_planner/api/v1/food.py
- [ ] T029 [P] [US2] Add nutrition confidence indicators to recipe display templates
- [ ] T030 [P] [US2] Implement meal characterization labels in nutrition calculator
- [ ] T031 [P] [US2] Create ingredient linking interface in recipe form template

**Checkpoint**: User Story 2 complete - nutrition displays with confidence and labels

---

## Phase 5: User Story 3 - Create and Manage Personal Profiles with Nutrition Goals (Priority: P1)

**Goal**: Allow creation of multiple profiles with nutrition targets and tolerance ranges for household use.

**Independent Test**: Create two profiles with different targets, compare a recipe against both profiles.

### Implementation for User Story 3

- [ ] T032 [P] [US3] Create Profile and ProfileTarget models in src/meal_planner/repository/sqlalchemy/models/profile.py
- [ ] T033 [P] [US3] Implement ProfileRepository protocol in src/meal_planner/repository/sqlalchemy/repositories/profile_repository.py
- [ ] T034 [US3] Create ProfileService with target comparison logic in src/meal_planner/services/profile_service.py
- [ ] T035 [P] [US3] Create Pydantic schemas for profile API in src/meal_planner/api/schemas/profile.py
- [ ] T036 [US3] Implement profile API endpoints in src/meal_planner/api/v1/profiles.py
- [ ] T037 [P] [US3] Add profile comparison to recipe detail template
- [ ] T038 [P] [US3] Create profile management templates in src/meal_planner/web/templates/profiles/

**Checkpoint**: User Story 3 complete - profiles support household nutrition goals

---

## Phase 6: User Story 4 - Plan Meals and See Weekly Nutrition Totals (Priority: P1)

**Goal**: Enable weekly meal planning with nutrition aggregation and leftover batch tracking.

**Independent Test**: Plan meals for a week, view weekly totals, mark a recipe as prepared in batch, track servings consumed.

### Implementation for User Story 4

- [ ] T039 [P] [US4] Create LeftoverBatch model in src/meal_planner/repository/sqlalchemy/models/batch.py
- [ ] T040 [P] [US4] Implement planning-related repository methods in existing repositories
- [ ] T041 [US4] Extend RecipeService with batch tracking logic
- [ ] T042 [P] [US4] Create Pydantic schemas for planning API in src/meal_planner/api/schemas/planning.py
- [ ] T043 [US4] Implement planning API endpoints in src/meal_planner/api/v1/planning.py
- [ ] T044 [P] [US4] Create weekly planner templates in src/meal_planner/web/templates/planning/
- [ ] T045 [P] [US4] Add batch preparation UI to recipe detail template

**Checkpoint**: User Story 4 complete - weekly planning with leftovers supported

---

## Phase 7: User Story 5 - Log Daily Meals and See Real-Time Progress (Priority: P1)

**Goal**: Provide fast daily logging with progress tracking against profile targets.

**Independent Test**: Log meals for a day, see real-time totals and progress bars, use repeat meal shortcuts.

### Implementation for User Story 5

- [ ] T046 [P] [US5] Create LogEntry model in src/meal_planner/repository/sqlalchemy/models/log.py
- [ ] T047 [P] [US5] Create MealTemplate model in src/meal_planner/repository/sqlalchemy/models/template.py
- [ ] T048 [P] [US5] Implement LogRepository protocol in src/meal_planner/repository/sqlalchemy/repositories/log_repository.py
- [ ] T049 [US5] Create LoggingService with daily totals calculation in src/meal_planner/services/logging_service.py
- [ ] T050 [P] [US5] Create Pydantic schemas for logging API in src/meal_planner/api/schemas/logging.py
- [ ] T051 [US5] Implement logging API endpoints in src/meal_planner/api/v1/logging.py
- [ ] T052 [P] [US5] Create daily log templates in src/meal_planner/web/templates/logging/
- [ ] T053 [P] [US5] Add progress visualization components to templates

**Checkpoint**: User Story 5 complete - daily logging with real-time progress

---

## Phase 8: User Story 6 - Receive Practical Suggestions to Adjust Meals (Priority: P1)

**Goal**: Generate rules-based suggestions for meal improvements based on profile gaps.

**Independent Test**: Log a meal short on protein, receive suggestion to add yogurt, apply it and see gap close.

### Implementation for User Story 6

- [ ] T054 [US6] Create SuggestionService with rules-based logic in src/meal_planner/services/suggestion_service.py
- [ ] T055 [P] [US6] Extend LoggingService with gap detection
- [ ] T056 [P] [US6] Create suggestion display components in templates
- [ ] T057 [P] [US6] Add suggestion API endpoints to existing routers

**Checkpoint**: User Story 6 complete - practical suggestions for meal adjustments

---

## Phase 9: User Story 7 - Cook from a Recipe in Distraction-Free Mode (Priority: P2)

**Goal**: Provide fullscreen cook mode with step-by-step navigation.

**Independent Test**: Open recipe in cook mode, navigate steps with taps, exit cleanly.

### Implementation for User Story 7

- [ ] T058 [P] [US7] Create cook mode template in src/meal_planner/web/templates/recipes/cook.html
- [ ] T059 [P] [US7] Add cook mode JavaScript for step navigation
- [ ] T060 [P] [US7] Implement cook mode route in recipes API

**Checkpoint**: User Story 7 complete - distraction-free cooking experience

---

## Phase 10: User Story 8 - Compare Meals Across Household Profiles (Priority: P2)

**Goal**: Show side-by-side nutrition fit for multiple profiles on the same meal.

**Independent Test**: Select recipe, view comparison for two profiles with different portion sizes.

### Implementation for User Story 8

- [ ] T061 [P] [US8] Extend profile comparison UI in recipe detail template
- [ ] T062 [P] [US8] Add portion size inputs to comparison view
- [ ] T063 [P] [US8] Update ProfileService for multi-profile comparisons

**Checkpoint**: User Story 8 complete - household profile comparisons

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Integration, UI polish, and system-wide improvements

- [ ] T064 [P] Implement global navigation and layout templates
- [ ] T065 [P] Add responsive design and mobile-friendly styling
- [ ] T066 [P] Implement data seeding for initial food library
- [ ] T067 [P] Add comprehensive input validation and error messages
- [ ] T068 [P] Optimize database queries and add indexes
- [ ] T069 [P] Add loading states and progressive enhancement
- [ ] T070 [P] Implement backup/export functionality
- [ ] T071 [P] Add help/tooltips for complex features
- [ ] T072 [P] Performance testing and optimization
- [ ] T073 [P] Accessibility improvements (WCAG compliance)
- [ ] T074 [P] Final integration testing across all user stories

**Checkpoint**: Product ready for personal use validation

---

## Dependencies

**Story Completion Order** (sequential dependencies):
1. US1 (foundation for all recipe operations)
2. US2 (depends on US1 for recipe nutrition)
3. US3 (profiles needed for comparisons)
4. US4 (depends on US1 for recipes, US3 for profiles)
5. US5 (depends on US1/US2 for meals, US3 for targets)
6. US6 (depends on US5 for logging, US3 for gaps)
7. US7 (depends on US1 for recipes)
8. US8 (depends on US3 for profiles, US2 for nutrition)

**Parallel Opportunities**:
- Within each story: Model creation, repository, service, API, templates can often run in parallel
- Across stories: US1 and US3 can start simultaneously after foundation
- US7 and US8 can be implemented in parallel after their dependencies

**Suggested MVP Scope**: Complete US1-US6 (all P1 stories) for core functionality. US7-US8 as P2 enhancements.

---

## Implementation Strategy

**MVP First**: Focus on US1-US6 for core recipe + nutrition + planning + logging loop. Each story delivers independent value.

**Incremental Delivery**: Implement one story at a time, ensuring each is fully functional before moving to the next.

**Testing Approach**: Manual testing per story checkpoint. Integration testing in final phase.

**Risk Mitigation**: Foundation phase ensures stable base. Parallel tasks within stories accelerate development.
---

## Testing & Validation

**Master Test Report**: See [TEST_REPORT.md](../../tests/TEST_REPORT.md)  
**Validation & Commands**: See [VALIDATION.md](../../VALIDATION.md)  
**Testing Strategy**: See [TESTING.md](./TESTING.md)

Phase 1–2 foundations include **45 unit tests** covering critical business logic (nutrition, conversions, search, sessions).

All tests passing. ✅ Ready for Phase 3 (User Story 1: Recipe CRUD).

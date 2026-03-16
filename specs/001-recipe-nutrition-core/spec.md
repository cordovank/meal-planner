# Feature Specification: Recipe Home & Nutrition-Aware Meal Planner — Phase 1 MVP

**Feature Branch**: `001-recipe-nutrition-core`  
**Created**: 2026-03-16  
**Status**: Draft  
**Input**: User description: "MPP is a local-first, web-based recipe home and nutrition-aware meal planning companion. It enables users to preserve homemade recipes, calculate and interpret nutrition, plan meals across a week/month, log daily intake, and receive practical improvement suggestions — all grounded in personal cooking behavior, pantry reality, and household context."

## Clarifications

### Session 2026-03-16
- Q: Should we include Open Food Facts as an additional primary nutrition data source alongside USDA FoodData Central, with flexibility to add/update when needed? → A: Use Open Food Facts as primary, USDA FoodData Central as secondary fallback.

---

## User Scenarios & Testing

### User Story 1 — Preserve and Organize Homemade Recipes (Priority: P1)

**Description:**  
A home cook wants to save family recipes, kitchen experiments, and meal prep patterns in a personal, organized collection. They should be able to capture recipes at any stage of documentation — from rough notes to fully structured recipes — and organize them for easy retrieval and reuse.

**Why this priority:**  
Recipes are the emotional core and foundation of the product. All other features depend on having a recipe library. A user can derive complete value from this alone: a personal cookbook.

**Independent Test:**  
Can be fully tested by: user creates a new recipe with title, ingredients, instructions, and tags → recipe appears in list → user retrieves, edits, and deletes the recipe. Delivers standalone value as a recipe storage and organization tool.

**Acceptance Scenarios:**

1. **Given** a user in a fresh app, **When** they create a recipe with title, ingredient list (with amounts/units), numbered instructions, and tags, **Then** the recipe is saved and appears in the recipe list.
2. **Given** a user with saved recipes, **When** they search by recipe name or ingredient, **Then** matching recipes appear in results.
3. **Given** a saved recipe, **When** user adds/edits/removes ingredients or instructions, **Then** changes persist without losing the recipe.
4. **Given** a recipe with inline notes (e.g., "too salty last time, reduce salt by half"), **When** user saves the note, **Then** the note remains attached and visible on subsequent views.
5. **Given** a user creating a recipe, **When** they mark it as "draft" state and save partial data (e.g., only a title and raw notes), **Then** the recipe is saved without error and flagged as incomplete.
6. **Given** a user with multiple recipes, **When** they add the same recipe to two different collections (e.g., "Weeknight Dinners" and "High Protein"), **Then** the recipe appears in both collections.
7. **Given** a saved recipe, **When** user scales it from 4 servings to 8 servings, **Then** all ingredient amounts are doubled and nutrition is recalculated proportionally.

---

### User Story 2 — Understand Recipe and Meal Nutrition with Confidence (Priority: P1)

**Description:**  
A nutrition-conscious cook wants to see how much protein, carbs, fat, and calories are in their recipes and meals. They want to understand the confidence level of the nutrition data (is it from a food label, estimated, or calculated?) so they can trust the numbers and make informed decisions.

**Why this priority:**  
Nutrition calculation is the bridge between recipe storage and personalized guidance. Without it, the product cannot help users make goal-aligned meal decisions. Confidence displays are essential to the trust-first positioning.

**Independent Test:**  
Can be fully tested by: user views a recipe with ingredients linked to nutrition data → nutrition summary displays (calories, protein, carbs, fat, fiber, added sugar) per serving → confidence icons show source of each ingredient's nutrition → interpretation label appears (e.g., "high protein, balanced carbs").

**Acceptance Scenarios:**

1. **Given** a recipe with all ingredients linked to the food library, **When** user views the recipe, **Then** total nutrition (calories, protein, carbs, fat, fiber, added sugar, sodium) displays for the full batch and per serving.
2. **Given** nutrition displayed on a recipe, **When** user scales the recipe, **Then** per-serving values remain the same AND total batch values scale proportionally.
3. **Given** a recipe with mixed ingredient confidence (one ingredient from a food label, one user-created), **When** user views the recipe nutrition, **Then** a confidence indicator shows mixed sources and warns that the total may be incomplete.
4. **Given** a recipe with sufficient nutrition data, **When** user views it, **Then** an automatic label appears (e.g., "high-protein", "high-added-sugar", "balanced") based on macro profile.
5. **Given** a recipe with missing nutrition for one or more ingredients, **When** user views the recipe, **Then** nutrition totals display for known ingredients only, with a clear "incomplete" indicator and a message: "Nutrition includes X known ingredients; Y still need data."
6. **Given** viewing a recipe's nutrition, **When** user hovers over an ingredient's nutrition contribution, **Then** they see the ingredient name, its nutrition values, and the source confidence (label, barcode scan, user-entered, estimated).
7. **Given** a user in the ingredient library, **When** they create a custom food entry with manual nutrition data, **Then** that food can be used in recipes and marked with "user-created" provenance.

---

### User Story 3 — Create and Manage Personal Profiles with Nutrition Goals (Priority: P1)

**Description:**  
Two people live in the same household with different nutrition goals: one tracking protein for fitness, the other watching added sugar for health reasons. They each need a profile with independent targets for calories, macros, and nutrient tolerances. The system should show whether a meal fits each profile's range.

**Why this priority:**  
Personalization enables the meal planning and feedback loop. Tolerance ranges (not binary targets) make the experience less punitive and more realistic. Household comparison is a key differentiator.

**Independent Test:**  
Can be fully tested by: user creates Profile A (150g protein, 50g fat, 200g carbs, added sugar <25g, with ±10% tolerance) → creates Profile B (different macros, same process) → selects a profile as default → views a meal and sees "fits Profile A" or "protein 5g short for Profile B".

**Acceptance Scenarios:**

1. **Given** a fresh app, **When** user creates a named profile (e.g., "Me", "Partner") with calorie target and macro targets (protein, carbs, fat), **Then** the profile is saved and becomes available for meal comparisons.
2. **Given** a saved profile, **When** user sets tolerance ranges (e.g., "protein target 150g ±15g"), **Then** the app treats values within this range as "on target" and only flags values outside the range.
3. **Given** a user with two profiles, **When** they view a recipe and select "compare profiles", **Then** they see side-by-side: Recipe fits Profile A? (yes/within range). Recipe fits Profile B? (yes/exceeding added sugar).
4. **Given** a profile without an explicit target (e.g., no added sugar target set), **When** comparing a meal to that profile, **Then** the meal uses a reasonable default reference (e.g., WHO guidance: 25g/day added sugar) and shows comparison.
5. **Given** a user's default profile, **When** they log meals for a day, **Then** daily totals compare against the default profile's targets without requiring profile selection per meal.

---

### User Story 4 — Plan Meals and See Weekly Nutrition Totals (Priority: P1)

**Description:**  
A meal planner wants to build a week of meals from their saved recipes, see total nutrition across the week, and identify gaps (e.g., "this week is low in fiber"). They want to prepare batches of food and track how servings are consumed throughout the week (leftovers awareness).

**Why this priority:**  
Planning is the primary forward-looking feature. Without it, the app is reactive (logging only). Planning enables confidence and intentionality. Leftover tracking reflects real home cooking.

**Independent Test:**  
Can be fully tested by: user creates a weekly plan by selecting recipes for breakfast/lunch/dinner/snacks across 7 days → views total weekly nutrition summed across all meals → notices a gap → reschedules meals or adjusts portions → weekly totals update → prepares a 4-serving batch on Monday → system tracks as "4 servings prepared" and allows decrementing as servings are consumed.

**Acceptance Scenarios:**

1. **Given** a recipe library, **When** user opens the weekly planner and clicks "Add meal" for Monday breakfast, **Then** a recipe picker appears showing favorites, recent recipes, and search.
2. **Given** a populated weekly plan, **When** user views the week overview, **Then** daily and weekly totals display (calories, protein, carbs, fat, added sugar) vs. the user's profile targets.
3. **Given** a weekly plan, **When** user identifies that Tuesday is low in protein, **Then** a "suggested add-ons" list appears showing snacks or side dishes from their recipe library that would close the gap.
4. **Given** a Monday dinner recipe with 8 servings marked as "prepared in batch", **When** user logs Monday dinner as 1 serving, **Then** the system shows "7 servings remaining" for this batch.
5. **Given** remaining servings from Monday's batch, **When** user logs Wednesday dinner and selects to use leftovers from Monday, **Then** the batch counter decrements and nutrition is correctly attributed.
6. **Given** a weekly plan, **When** user reschedules a meal from Tuesday to Thursday, **Then** the meal and its nutrient contribution move to the new day and weekly totals update.
7. **Given** a weekly plan with multiple profiles (e.g., user + partner), **When** a single meal appears for both, **Then** user can set different portion sizes per profile and see individual nutrition fit.

---

### User Story 5 — Log Daily Meals and See Real-Time Progress (Priority: P1)

**Description:**  
A user wants to quickly log what they're eating throughout the day (breakfast, lunch, dinner, snacks) and see real-time totals against their daily targets. Logging should be fast for repeat meals (yesterday's lunch again) and should support quick-add patterns.

**Why this priority:**  
The daily loop is where the product becomes a habit. Low friction logging makes users return. Real-time visual feedback (progress bars, target ranges) is the core motivation.

**Independent Test:**  
Can be fully tested by: user logs breakfast (1min), lunch (1min using yesterday's meal shortcut), snack (instant from recent items), dinner (2min searching for a recipe) → sees daily totals (calories 2100/2200 target, protein 142g/150g target, added sugar 20g/25g target) → understands where they stand without confusion.

**Acceptance Scenarios:**

1. **Given** today's log view, **When** user clicks "Add meal" for breakfast, **Then** a meal entry form appears with quick shortcuts (recent meals, favorites, meal templates) above a full search.
2. **Given** a user who logged the same meal yesterday, **When** they click "Repeat yesterday's lunch", **Then** the same meal is logged for today without re-searching.
3. **Given** a logged meal with multiple ingredients, **When** user adjusts the portion from 1 serving to 1.5 servings, **Then** nutrition updates and daily totals recalculate immediately.
4. **Given** a daily log with 3+ meals, **When** user views the day summary, **Then** target ranges appear visually (progress bars or equivalent) showing consumed / target / tolerance band for calories, protein, carbs, fat, added sugar.
5. **Given** daily totals displayed, **When** user is below target in any macro (e.g., protein 130/150g), **Then** the gap is visual (color, icon) and text states: "You're 20g short on protein today. See suggestions below."
6. **Given** suggestions displayed for a gap, **When** user clicks a suggestion (e.g., "Add Greek yogurt"), **Then** the food is added to the meal, nutrition updates, and daily totals close the gap.
7. **Given** a logged meal created from a batch (prepared on Monday, logged on Wednesday), **When** user views the meal, **Then** the source is clear: "Leftover from Monday's batch (3 servings prepared, 2 consumed, 1 remaining)."

---

### User Story 6 — Receive Practical Suggestions to Adjust Meals (Priority: P1)

**Description:**  
When a user's meal or day doesn't align with their goals, instead of just seeing a warning, they should get constructive suggestions: "Add protein via yogurt (fits your pantry) → adds 15g protein, doesn't spike added sugar" or "Swap the granola for plain oats → saves 8g added sugar." Suggestions respect dietary preferences and pantry realities.

**Why this priority:**  
This transforms the product from a passive tracker to an active companion. Suggestions with clear rationale build trust and actionability. This is the primary differentiator from existing trackers.

**Independent Test:**  
Can be fully tested by: user logs a meal that's low in protein → system detects gap vs. profile target and tolerance → shows 3 suggestions (all recipes/foods from user's library or pantry) → user selects one → nutrition updates → gap closes. User can see why each suggestion was chosen.

**Acceptance Scenarios:**

1. **Given** a meal with insufficient protein (e.g., 12g total, target 30g per meal), **When** user saves the meal, **Then** a suggestion appears: "This meal is low in protein. Add 20g of protein via: [Greek yogurt], [chicken breast], [protein powder]" with nutrition deltas shown.
2. **Given** a suggestion shown to user, **When** user hovers/clicks the suggestion, **Then** they see the rationale: "Greek yogurt: +15g protein, adds only 3g sugar (fits your added sugar target)."
3. **Given** a daily total that exceeds added sugar target (e.g., 30g consumed, 25g target), **When** user views the day, **Then** a suggestion appears: "Your added sugar is 5g over target. Consider: [swap afternoon snack from granola to nuts: save 8g sugar], [try sugarless yogurt instead of flavored]."
4. **Given** a suggestion involving a substitution, **When** user clicks "Try this swap", **Then** a preview shows old meal vs. new meal side-by-side (nutrition, ingredients, prep time).
5. **Given** multiple suggestions, **When** user applies one, **Then** remaining suggestions update or disappear if they're no longer relevant.
6. **Given** a user with dietary restrictions (e.g., nut allergy), **When** suggestions are shown, **Then** no suggestion includes nuts — the system respects profile exclusions.

---

### User Story 7 — Cook from a Recipe in Distraction-Free Mode (Priority: P2)

**Description:**  
When actively cooking, the user opens a recipe and enters "cook mode" — a full-screen, minimalist view with large text, ingredient checklist, and step-by-step navigation. Tap/click to advance, no clutter, readable from a distance.

**Why this priority:**  
This feature makes the product genuinely useful during active cooking (when it's most needed). Without it, the app is a planning/logging tool, not a cooking companion. Deferred to P2 but essential for the product soul.

**Independent Test:**  
Can be fully tested by: user opens a recipe, taps "Cook" button → full-screen view shows scaled ingredient list with checkboxes → one step displayed large → tap "Next" to advance → user completes all steps using this view → returns to normal view.

**Acceptance Scenarios:**

1. **Given** a recipe view, **When** user taps "Cook Mode", **Then** the app enters fullscreen with large text, no navigation chrome, and a step-by-step interface.
2. **Given** cook mode active, **When** user views the ingredient list, **Then** amounts are shown at the recipe's current scale, with optional checkboxes to mark as prepared.
3. **Given** cook mode showing a step, **When** user taps "Next", **Then** the next step displays. Tapping "Previous" shows the prior step.
4. **Given** cook mode active, **When** user taps and holds, **Then** a "return to normal view" button appears (quick exit without closing the app).
5. **Given** a recipe with timing notes (e.g., "prep 10 min" on one step), **When** cook mode displays that step, **Then** timing is shown prominently.

---

### User Story 8 — Compare Meals Across Household Profiles (Priority: P2)

**Description:**  
A couple with different needs uses the app together. When planning or cooking a shared meal, they want to see: "This pasta dish fits Mike's 150g protein target (yes, 42g protein) but not Sarah's <25g added sugar target (no, 18g added sugar — 7g over)." Suggestions can then help adapt the meal for balance.

**Why this priority:**  
Household support is a differentiator and real-world use case. Deferred to P2 but enabled from P1 data model.

**Independent Test:**  
Can be fully tested by: user creates two profiles with different targets → selects a recipe → clicks "Compare profiles" → sees side-by-side fit for each profile → identifies gaps → applies a suggestion and sees updated fit for both profiles.

**Acceptance Scenarios:**

1. **Given** a user with two household profiles (Profile A: 150g protein, Profile B: <25g added sugar), **When** they select a recipe and click "Compare", **Then** they see: Profile A: ✓ Fits (45g protein / 150g target). Profile B: ✗ Exceeds (28g added sugar / 25g target).
2. **Given** a meal that exceeds one profile's target, **When** user views comparison, **Then** a "Make this meal work for both" button appears showing adjustments (e.g., "serve Profile B a smaller portion with a side of unsweetened yogurt").
3. **Given** a weekly plan with a shared meal, **When** user sets different portion sizes for each profile, **Then** individual nutrition fit updates for each.

---

## Edge Cases

- **Incomplete nutrition data:** What if a recipe has 3 ingredients with full nutrition and 2 with no data? → System calculates partial nutrition, clearly marks as incomplete, and allows user to fill in missing data or accept the incomplete result.
- **Unit conversion precision:** What if a user scales a recipe from 4 servings to 3 servings, requiring 0.75 of an ingredient listed in tablespoons? → System converts and displays in simplest form (e.g., 3/4 tbsp or ~11 ml) with a note that exact measurement may require a scale.
- **Floating-point rounding in nutrition:** What if protein total is 149.7g and the profile target is 150g? → System treats this as within tolerance (no warning). The tolerance band absorbs small rounding differences.
- **Meal logging after midnight:** If a user logs meals for "yesterday" after midnight, are they added to yesterday or today? → UI always shows the date/day selector; if user logs after midnight without explicit selection, prompt confirms the intended date.
- **Profile targets with interdependencies:** If a user sets protein to 150g but macro percentages don't balance (total macros exceed calorie target), what happens? → On save, system validates and alerts user to the mismatch. Profile is not saved until conflict is resolved.
- **Meal prepared in batch but entire batch deleted:** If Monday's prepared batch is deleted mid-week, do subsequent meals referencing leftovers break? → System soft-deletes the batch and updates dependent meals to show "This item is no longer available" without data loss; user can mark the meal as completed or reassign to another recipe.

---

## Requirements

### Functional Requirements

**Recipe Management**
- **FR-001:** System MUST allow users to create recipes with: title (required), description (optional), ingredient list (each with name, amount, unit, notes, to_taste flag), ordered instructions, prep/cook time (optional), servings/batch size, and tags.
- **FR-002:** System MUST support recipe lifecycle states: `draft | pending_review | incomplete | finalized`. Users MUST be able to save recipes in draft state without completing all fields.
- **FR-003:** System MUST allow users to scale recipes by serving count or multiplier, auto-recalculating all ingredient amounts and nutrition values.
- **FR-004:** System MUST support unit conversion in-place (grams ↔ ounces, milliliters ↔ cups, teaspoons ↔ tablespoons) for recipe ingredients.
- **FR-005:** System MUST allow users to duplicate a recipe and optionally name it as a version (e.g., "original", "lighter", "high-protein") linked to a parent recipe.
- **FR-006:** System MUST provide full-text search across recipe names, ingredients, and tags. Search results MUST include partial matches.
- **FR-007:** System MUST support filtering recipes by: macro profile (high-protein, low-carb, etc.), meal type (breakfast, lunch, dinner, snack), dietary compatibility, prep/cook time, state, and ingredient availability.
- **FR-008:** System MUST support user-defined recipe collections (many-to-many). A recipe can belong to multiple collections. Collections MUST be reorderable.
- **FR-009:** System MUST allow users to mark recipes as favorites (first-class flag, not a collection).
- **FR-010:** System MUST allow users to attach timestamped notes to recipes (e.g., "too salty, reduce by half next time") and capture meal reflections (e.g., "very filling", "good post-workout").

**Nutrition Data & Calculation**
- **FR-011:** System MUST calculate total and per-serving nutrition for recipes with ingredients linked to the food library. Minimum nutrients: calories, protein, carbohydrates, total fat. Extended set: fiber, total sugar, added sugar, sodium, saturated fat.
- **FR-012:** System MUST treat added sugar as a first-class nutrition field (distinct from total sugar, always displayed, never optional).
- **FR-013:** System MUST display nutrition with confidence indicators based on data provenance: `label | barcode | user_confirmed | estimated | calculated`.
- **FR-014:** System MUST automatically generate meal characterization labels (e.g., "high-protein", "low-carb", "high-fiber", "high-added-sugar", "balanced") based on configurable nutrient thresholds.
- **FR-015:** System MUST provide plain-language interpretation of nutrition (e.g., "high protein but low fiber") relative to profile targets.
- **FR-016:** System MUST support creation and management of a local ingredient library with user-created custom foods (with manual nutrition entry).
- **FR-017:** System MUST accept ingredients with incomplete nutrition data and calculate partial totals with clear "incomplete" indicators.

**Profiles & Personalization**
- **FR-018:** System MUST allow users to create multiple profiles with: name, calorie target (optional), macro targets (protein, carbs, fat), tolerance ranges (e.g., ±10% or ±absolute), and optional notes.
- **FR-019:** System MUST support comparison of the same meal/recipe against two profiles simultaneously, showing fit/gap for each.
- **FR-020:** System MUST use tolerance ranges (not binary targets) for goal comparison, marking values as: `within_range | approaching | exceeding`.
- **FR-021:** System MUST apply default reasonable values for targets and tolerance ranges if user does not set them explicitly.
- **FR-022:** System MUST respect profile-level dietary restrictions (allergen exclusions, dislikes, foods to avoid) in suggestion generation.

**Meal Planning**
- **FR-023:** System MUST support weekly meal planning: users select recipes for breakfast, lunch, dinner, snacks across 7 days.
- **FR-024:** System MUST aggregate daily and weekly nutrition totals across all planned meals and compare against profile targets.
- **FR-025:** System MUST track prepared meal batches (e.g., "4 servings prepared Monday") and decrement as servings are logged/consumed.
- **FR-026:** System MUST allow users to log leftover batch usage and reassign the same prepared meal across multiple days without duplicating nutrition.
- **FR-027:** System MUST support rescheduling meals within a week while preserving nutrition linkage.

**Daily Logging**
- **FR-028:** System MUST provide a fast daily logging surface with meal slots (breakfast, lunch, dinner, snacks, custom).
- **FR-029:** System MUST include quick-entry shortcuts: recent meals, favorites, meal templates, and full search.
- **FR-030:** System MUST allow users to log a repeat meal in ≤3 interactions.
- **FR-031:** System MUST auto-calculate and display daily totals (calories, macros, added sugar, etc.) in real time as meals are logged.
- **FR-032:** System MUST show tolerance-range-based progress (consumed / target / tolerance band) visually and textually.
- **FR-033:** System MUST allow users to adjust portion sizes after logging and recalculate totals immediately.
- **FR-034:** System MUST save meal templates (e.g., "weekday routine", "training day") and apply them to any day with one action.

**Gap Detection & Suggestions**
- **FR-035:** System MUST identify macro and nutrient gaps at meal and daily levels, comparing actual intake against profile targets with tolerance ranges.
- **FR-036:** System MUST generate practical improvement suggestions: add-ons, snacks, substitutions, portion adjustments, and alternate meal options.
- **FR-037:** System MUST prioritize suggestions from: saved recipes → pantry ingredients → commonly used items → household-compatible foods (in Phase 2+).
- **FR-038:** System MUST include a human-readable rationale for every suggestion (e.g., "Greek yogurt: +15g protein, adds only 3g sugar, fits your target").
- **FR-039:** System MUST exclude suggestions that violate profile allergies/restrictions.
- **FR-040:** Every gap description MUST be plain-language and non-judgmental (e.g., "you're 20g short on protein today" NOT "you failed to hit protein target").

**Cook Mode**
- **FR-041:** System MUST provide a dedicated fullscreen "cook mode" view accessible from any recipe in ≤2 taps.
- **FR-042:** Cook mode MUST display: large readable text, ingredient list with scaled amounts and checkboxes, step-by-step navigation (one step at a time).
- **FR-043:** Cook mode MUST allow tap/click navigation between steps without requiring precise touch targets.
- **FR-044:** Cook mode MUST reflect the recipe's current scale (if user scaled to 8 servings before entering cook mode).

### Key Entities

- **Recipe:** Represents a homemade recipe. Fields: id (UUID), user_id (FK), title, description, state (draft/pending_review/incomplete/finalized), ingredient list, ordered steps, prep_time, cook_time, base_servings, version metadata (parent_recipe_id, version_label), tags, created_at, updated_at, deleted_at.

- **RecipeIngredient:** Links a specific ingredient to a recipe. Fields: id (UUID), recipe_id (FK), food_entry_id (FK, nullable), name, amount (nullable), unit (nullable), to_taste (boolean), optional (boolean), notes, sort_order.

- **FoodEntry:** Represents a food or ingredient in the local library (from USDA, barcode scan, or user-created). Fields: id (UUID), user_id (FK, nullable for system entries), name, brand (optional), category (optional), source_type (usda/label/barcode/user_created/calculated), source_id (optional), is_custom (boolean), created_at, updated_at, deleted_at.

- **NutritionRecord:** Contains nutrition data for a FoodEntry. Fields: id (UUID), food_entry_id (FK), serving_size, serving_unit, calories, protein_g, carbohydrates_g, fat_g, fiber_g, total_sugar_g, added_sugar_g, sodium_mg, saturated_fat_g, source_type (label/barcode/user_confirmed/estimated/calculated, non-null), created_at, updated_at.

- **Profile:** Represents a user's personalized nutrition goals and preferences. Fields: id (UUID), user_id (FK), name, calorie_target (optional), calorie_tolerance, macro_targets (protein/carbs/fat with tolerance ranges), notes, is_default (boolean), created_at, updated_at, deleted_at.

- **ProfileTarget:** Per-nutrient target with tolerance. Fields: id (UUID), profile_id (FK), nutrient_key (protein_g, fat_g, added_sugar_g, etc.), target_value, tolerance_value (±absolute), unit (g/mg/kcal).

- **LogEntry:** Represents a logged meal on a specific day. Fields: id (UUID), user_id (FK), profile_id (FK), date, meal_slot (breakfast/lunch/dinner/snack/custom), recipe_id (FK, can be null if custom meal), portion_size, created_at, updated_at, deleted_at.

- **LeftoverBatch:** Tracks a prepared batch of food. Fields: id (UUID), recipe_id (FK), initial_servings, prepared_date, servings_remaining, created_at, updated_at, deleted_at.

- **MealTemplate:** A saved reusable meal combination. Fields: id (UUID), user_id (FK), name, meal_items (list of recipe_id + portion). Linked to LogEntry for one-click daily application.

- **RecipeNote:** Timestamped notes attached to a recipe. Fields: id (UUID), recipe_id (FK), note_text, created_at, updated_at, deleted_at.

---

## Success Criteria

### Measurable Outcomes

- **SC-001:** Developer uses MPP as personal primary recipe/meal tool with ≥5 recipes created, ≥1 meal plan built per week, ≥6 days/week of daily logging over a 4-week validation period.

- **SC-002:** All recipe management workflows (create, edit, scale, search, collections) complete without errors. Recipe retrieval time <500ms for libraries up to 100 recipes.

- **SC-003:** Nutrition calculation accuracy: all calculated values (per-serving, batch totals, scaled meals) match hand-calculated values to within ±1 calorie and ±0.5g per macro. Zero instances of silently incorrect nutrition displayed.

- **SC-004:** Daily logging surface: repeat meal logging in <60 seconds (using recent/shortcut patterns). New meal search and add in <2 minutes.

- **SC-005:** Gap detection and suggestions: every gap >5% of target triggers a suggestion. Every suggestion includes a rationale string. 0 suggestions violate profile restrictions.

- **SC-006:** Data confidence: every nutrition display clearly shows source (label, barcode, user-created, estimated, calculated). Partial completeness indicators are visible inline (not in hidden details).

- **SC-007:** Visual progress: daily totals display with clear, color-blind accessible progress indicators for consumed/target/tolerance band. No reliance on color alone for status.

- **SC-008:** Meal characterization: 95%+ of finalized recipes display at least one accurate characterization label (high-protein, balanced, etc.) corresponding to their actual nutrient profile.

- **SC-009:** Cook mode: accessible from any recipe in ≤2 taps, displays large readable text, step navigation completes without errors or requiring precise touch targets.

- **SC-010:** Data portability: all entities use UUID primary keys and versioned migrations. PostgreSQL schema drop-in replacement possible with zero business logic changes (validated with manual schema migration test).

- **SC-011:** User satisfaction: developer reports that the product feels calm, intuitive, and faster than alternative tools for daily recipe storage and meal planning.

---

## Assumptions & Dependencies

### Assumptions

- **[A01]** Developer is the initial and primary user for Phase 1. Product-market fit will be validated through daily personal use.
- **[A02]** SQLite is sufficient for local single-user/small household use (Phase 1 & 2).
- **[A03]** Open Food Facts is available as the primary nutrition data source; USDA FoodData Central as secondary fallback; licensing review required.
- **[A04]** Unit conversion reference data (g/oz, ml/cup mappings) is available and accurate.
- **[A05]** Server-side rendering (Jinja2 + minimal JS) is acceptable for Phase 1 UX complexity.
- **[A06]** Cloud deployment (Phase 3) is a real possibility; all Phase 1 decisions preserve the cloud-portable data model.
- **[A07]** No external API calls required in Phase 1; all data and logic are locally packaged or computed.

### External Dependencies

- **Open Food Facts:** Primary nutrition reference data (licensing, access method through Open Food Facts API; https://openfoodfacts.github.io/openfoodfacts-server/api/).
- **USDA FoodData Central:** Secondary fallback nutrition reference data (licensing, access method for Foundation Foods TBD).
- **SQLAlchemy 2.0 + async support:** ORM and database abstraction.
- **FastAPI:** HTTP routing and request validation.
- **Pydantic v2:** Request/response schema validation.
- **Jinja2 + HTMX:** Server-rendered templates with minimal frontend complexity.
- **Alembic:** Database migration versioning.
- **SQLite FTS5:** Full-text search (Phase 1); PostgreSQL tsvector (Phase 3).

---

## Constraints & Out-of-Scope

### Constraints

- **Local-first, no cloud in Phase 1:** No public authentication, no cloud sync, no third-party integrations.
- **Solo developer capacity:** Sequential implementation, no parallelization. Scope must fit one person's 6-month timeline.
- **SQLite in Phase 1:** Single-writer limitation; no concurrent multi-user support.
- **No BMI-based logic, no medical claims:** All nutrition guidance is educational and goal-aligned, never clinical or prescriptive.
- **Supportive tone only:** No judgmental language, no punitive mechanics, no shame-based engagement patterns.

### Out of Scope (Phase 2+)

- Barcode scanning / OCR (Phase 2)
- Pantry tracking and inventory (Phase 2)
- Wearable/health platform integrations (Phase 3)
- Cloud deployment and public authentication (Phase 3)
- AI-assisted meal logging or suggestions (Phase 3)
- Monetization infrastructure (Phase 3)

---

## Notes

- This specification is informed by MPP Requirements v3, Product Vision v1, FoodDB reference patterns, and the project Constitution (1.0.0, ratified 2026-03-16).
- The feature encompasses 21 Phase 1 must-have capabilities from the requirements catalog (F01-F05, F07-F12, F15-F17, F19-F22, F27-F28, F31).
- Specification validation and clarification workflow is next: use `/speckit.clarify` to surface any ambiguities requiring user decision.

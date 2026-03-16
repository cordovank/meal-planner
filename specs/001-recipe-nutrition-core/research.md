# Research Findings: Recipe Home & Nutrition-Aware Meal Planner — Phase 1 MVP

**Date**: 2026-03-16 | **Context**: Phase 1 MVP implementation planning

## Decision: Open Food Facts as Primary Nutrition Data Source

**Rationale**: Open Food Facts provides comprehensive, open-source nutrition data with global coverage, user-contributed entries, and permissive licensing. As primary source, it enables broad ingredient matching and community-driven data quality. USDA FoodData Central serves as secondary fallback for US-specific or high-precision needs.

**Alternatives Considered**:
- USDA only: Limited to US foods, potential licensing restrictions for bundling
- Custom database: Too resource-intensive for Phase 1, no existing data
- Multiple APIs: Open Food Facts covers 80%+ of common ingredients, reducing complexity

## Decision: USDA FoodData Central as Secondary Fallback

**Rationale**: Provides authoritative, government-verified nutrition data for US foods. Used when Open Food Facts lacks coverage or precision. Licensing review confirms acceptable for local bundling in Phase 1.

**Alternatives Considered**:
- No fallback: Would limit ingredient coverage and data quality
- Other databases (e.g., Nutritionix): Paid APIs not suitable for local-first Phase 1

## Decision: Unit Conversion Reference Data

**Rationale**: Use established conversion tables from reliable sources (e.g., USDA conversion factors, standard culinary references). Implement as static lookup tables in code for Phase 1, with configurable precision.

**Alternatives Considered**:
- Dynamic API calls: Not local-first compatible
- User-defined conversions: Too complex for Phase 1 UX

## Decision: Fuzzy Search Implementation

**Rationale**: RapidFuzz library provides fast, accurate fuzzy matching for ingredient names. Use trigram-based similarity scoring with configurable thresholds (e.g., 80% similarity for suggestions).

**Alternatives Considered**:
- Exact match only: Poor UX for varied ingredient naming
- Full FTS5: Overkill for Phase 1 scale, adds complexity

## Decision: Nutrition Calculation Precision

**Rationale**: Use floating-point arithmetic with 2 decimal places for display, 4 decimals for internal calculations. Round consistently at display boundaries to avoid accumulation errors.

**Alternatives Considered**:
- Integer-based (e.g., grams * 100): More complex, no significant precision benefit
- Arbitrary precision: Unnecessary overhead for nutrition data

## Decision: Profile Tolerance Defaults

**Rationale**: Calorie tolerance: ±100 kcal (10% of typical 2000 kcal target). Protein/Carbs/Fat: ±15% absolute. Added sugar: WHO guideline 25g/day with ±20% tolerance. Configurable in settings.

**Alternatives Considered**:
- No defaults: Forces user configuration, poor UX
- Fixed percentages: Less flexible than absolute ranges for some nutrients

## Decision: Meal Characterization Labels

**Rationale**: High-protein: >25g per 500 kcal. High-added-sugar: >10g per 500 kcal. Balanced: within 20% of macro distribution targets. Labels based on per-serving density.

**Alternatives Considered**:
- Absolute thresholds: Not scalable across recipe sizes
- User-configurable: Too complex for Phase 1

## Decision: Leftover Batch Tracking

**Rationale**: Simple counter-based system: initial_servings, servings_remaining. Decrement on consumption, soft-delete when zero. No complex expiration logic in Phase 1.

**Alternatives Considered**:
- Date-based expiration: Adds complexity, not core to MVP
- Quantity-based: Overkill for serving-level tracking

## Decision: Cook Mode UX

**Rationale**: Fullscreen overlay with large text (24pt+), ingredient checkboxes, step navigation. Tap/click to advance, no scroll required. Exit with hold gesture or explicit button.

**Alternatives Considered**:
- Split-screen: Less focused for cooking
- Voice navigation: Requires additional dependencies, Phase 2

## Decision: Suggestion Generation Rules

**Rationale**: Rules-based engine with pantry-aware matching. Prioritize: saved recipes → common pantry items → household staples. Include nutrition deltas and plain-language rationale.

**Alternatives Considered**:
- AI-generated: Not Phase 1 scope, requires external calls
- Static suggestions: Less personalized than pantry-aware

## Decision: Data Confidence Indicators

**Rationale**: Four levels: label (product packaging), barcode (scanned), user_confirmed (manual entry verified), estimated (calculated). Display as icons with tooltips showing source details.

**Alternatives Considered**:
- Numeric scores: Less intuitive than categorical
- No display: Violates trust principle

## Decision: Recipe State Lifecycle

**Rationale**: Draft (no validation), incomplete (partial data), pending_review (ready for check), finalized (complete and validated). Users can save at any state.

**Alternatives Considered**:
- Binary draft/final: Less granular for user workflow
- Auto-promotion: Removes user control

## Decision: Search and Filtering

**Rationale**: Full-text search on title/ingredients/tags. Filters: macro profile (high-protein, etc.), meal type, prep time, state. Use FTS5 for SQLite performance.

**Alternatives Considered**:
- No search: Poor usability
- External search engine: Not local-first

## Decision: Version Control for Recipes

**Rationale**: Parent-child relationship with version_label (e.g., "original", "low-sodium"). Duplicate creates new version. No branching complexity in Phase 1.

**Alternatives Considered**:
- Git-like versioning: Overkill for recipes
- No versioning: Loses iteration history
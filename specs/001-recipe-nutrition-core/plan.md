# Implementation Plan: Recipe Home & Nutrition-Aware Meal Planner — Phase 1 MVP

**Branch**: `001-recipe-nutrition-core` | **Date**: 2026-03-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-recipe-nutrition-core/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

MPP is a local-first, web-based recipe home and nutrition-aware meal planning companion. It enables users to preserve homemade recipes, calculate and interpret nutrition, plan meals across a week/month, log daily intake, and receive practical improvement suggestions — all grounded in personal cooking behavior, pantry reality, and household context. Technical approach: Modular monolith with layered architecture (API → Services → Repository → DB), Pydantic contracts at boundaries, server-side rendering with Jinja2 + HTMX, SQLite for Phase 1 storage with PostgreSQL migration path.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2, Jinja2 + HTMX  
**Storage**: SQLite (Phase 1), PostgreSQL (Phase 3, zero business logic changes)  
**Testing**: pytest + pytest-asyncio, pytest-cov, httpx  
**Test Report**: See [tests/TEST_REPORT.md](/tests/TEST_REPORT.md) for Phase 1–4 test results (141 tests, 83% coverage, all passing)
**Target Platform**: Web application (localhost or private home server)  
**Project Type**: Web service (local-first, single-user/small household)  
**Performance Goals**: <500ms recipe retrieval for 100 recipes, <1s nutrition calculation per recipe, <60s daily logging  
**Constraints**: Local-first deployment, SQLite single-writer limitation, no external API calls in Phase 1, server-side rendering acceptable  
**Scale/Scope**: 100 recipes, daily meal logging, weekly planning, nutrition calculations for 8 entities

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Assessment

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Recipe-First Design | ✅ Compliant | Spec prioritizes recipes as core, nutrition as enhancement |
| II. Supportive and Non-Punitive Language | ✅ Compliant | Spec requires non-judgmental language, tolerance ranges, constructive suggestions |
| III. Architecture Dependency Direction | ✅ Compliant | API → Services → Repository → DB enforced |
| IV. Pydantic Contracts at Boundaries | ✅ Compliant | All API I/O uses Pydantic schemas |
| V. Nutrition Calculations in Service Layer Only | ✅ Compliant | Calculations in service layer, added_sugar_g first-class, source_type required |
| VI. Entity Standards | ✅ Compliant | UUID PKs, audit timestamps, soft deletes on all entities |
| VII. Phase 1 Scope Constraints | ✅ Compliant | SQLite only, no cloud/AI/Stripe, rules-based suggestions |
| VIII. Testing Discipline | ✅ Compliant | Unit tests for calculations/verifiers, integration for APIs |

**Gate Status**: PASS — No violations detected. All principles aligned with spec and technical approach.

## Project Structure

### Documentation (this feature)

```text
specs/001-recipe-nutrition-core/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
└── meal_planner/                # importable package
    ├── __init__.py
    ├── config.py                # pydantic-settings config
    ├── main.py                  # FastAPI application factory
    ├── api/
    │   ├── __init__.py
    │   ├── schemas/             # Pydantic request/response models
    │   │   └── __init__.py
    │   └── v1/                  # versioned API routers
    │       └── __init__.py
    ├── domain/                  # domain entities and value objects
    │   └── __init__.py
    ├── services/                # business logic layer
    │   └── __init__.py
    ├── repository/
    │   ├── __init__.py
    │   ├── migrations/          # Alembic migration chain
    │   │   ├── README
    │   │   ├── env.py
    │   │   ├── script.py.mako
    │   │   └── versions/
    │   └── sqlalchemy/          # concrete SQLAlchemy implementations
    │       └── __init__.py
    ├── infra/
    │   ├── __init__.py
    │   ├── ai/                  # Phase 3: LLM client adapters
    │   ├── ocr/                 # Phase 2: Tesseract + Ollama backends
    │   └── search/              # FTS5 / fuzzy search implementation
    │       └── __init__.py
    └── web/
        ├── __init__.py
        ├── static/
        └── templates/
```

**Structure Decision**: Single project web application structure. Modular monolith with layered service boundaries, deployed as a single process for Phase 1. API-first design enables future mobile clients. Directories match scaffolding report layout.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations to justify.

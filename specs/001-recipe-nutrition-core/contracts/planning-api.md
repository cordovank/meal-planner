# API Contracts: Meal Planning

**Context**: REST API endpoints for weekly planning and batch tracking

## Endpoints

### GET /api/v1/plan/{week_start}
Get weekly plan.

**Path**: week_start as YYYY-MM-DD (Monday)

**Response**: 200 OK
```json
{
  "week_start": "2026-03-16",
  "days": [
    {
      "date": "2026-03-16",
      "meals": [
        {
          "meal_slot": "dinner",
          "recipe_id": "uuid",
          "title": "Chicken Stir Fry",
          "servings": 4,
          "batch_prepared": true,
          "batch_remaining": 2
        }
      ],
      "totals": {...}
    }
  ],
  "weekly_totals": {...},
  "gaps": [...]
}
```

### POST /api/v1/plan/{date}/meals
Add meal to plan.

**Request Body**:
```json
{
  "meal_slot": "lunch",
  "recipe_id": "uuid",
  "servings": 2
}
```

**Response**: 201 Created

### DELETE /api/v1/plan/{date}/meals/{id}
Remove meal from plan.

**Response**: 204 No Content

### POST /api/v1/plan/{date}/meals/{id}/batch
Mark meal as batch prepared.

**Request Body**:
```json
{
  "prepared_servings": 6
}
```

**Response**: 200 OK

### POST /api/v1/plan/batch/consume
Consume from batch.

**Request Body**:
```json
{
  "batch_id": "uuid",
  "servings_consumed": 1,
  "date": "2026-03-17",
  "meal_slot": "lunch"
}
```

**Response**: 200 OK (updated batch)

### POST /api/v1/plan/{date}/reschedule
Move meal to different date.

**Request Body**:
```json
{
  "meal_id": "uuid",
  "new_date": "2026-03-18",
  "new_slot": "dinner"
}
```

**Response**: 200 OK

### GET /api/v1/plan/suggestions
Get planning suggestions.

**Query**: date, meal_slot

**Response**: 200 OK
```json
{
  "favorites": [...],
  "recent": [...],
  "by_gap": [
    {
      "recipe_id": "uuid",
      "title": "Salmon",
      "rationale": "High in protein (+25g), fits your target"
    }
  ]
}
```
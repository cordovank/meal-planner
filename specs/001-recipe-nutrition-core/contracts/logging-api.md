# API Contracts: Daily Logging

**Context**: REST API endpoints for meal logging and daily progress

## Endpoints

### GET /api/v1/log/{date}
Get daily log for specific date.

**Response**: 200 OK
```json
{
  "date": "2026-03-16",
  "profile_id": "uuid",
  "meals": [
    {
      "id": "uuid",
      "meal_slot": "breakfast",
      "recipe_id": "uuid",
      "recipe_title": "Oatmeal",
      "portion_size": 1.0,
      "nutrition": {...},
      "logged_at": "2026-03-16T08:00:00Z"
    }
  ],
  "totals": {
    "calories": 1850,
    "protein_g": 85,
    "carbohydrates_g": 250,
    "fat_g": 65,
    "added_sugar_g": 15
  },
  "progress": {
    "calories": {"consumed": 1850, "target": 2000, "status": "within_range"},
    "protein_g": {"consumed": 85, "target": 150, "status": "approaching"}
  },
  "gaps": [
    {
      "nutrient": "protein_g",
      "short_by": 65,
      "suggestions": ["Add chicken breast (+30g)", "Greek yogurt (+15g)"]
    }
  ]
}
```

### POST /api/v1/log/{date}/meals
Log a new meal.

**Request Body**:
```json
{
  "meal_slot": "lunch",
  "recipe_id": "uuid",
  "portion_size": 1.5,
  "notes": "Used leftovers"
}
```

**Response**: 201 Created (meal log entry)

### PUT /api/v1/log/meals/{id}
Update logged meal.

**Request Body**: Same as POST

**Response**: 200 OK (updated meal)

### DELETE /api/v1/log/meals/{id}
Remove logged meal.

**Response**: 204 No Content

### POST /api/v1/log/{date}/repeat
Repeat meal from another date.

**Request Body**:
```json
{
  "from_date": "2026-03-15",
  "meal_slot": "lunch"
}
```

**Response**: 201 Created (repeated meal)

### GET /api/v1/log/recent
Get recent meals for quick logging.

**Response**: 200 OK
```json
{
  "meals": [
    {
      "recipe_id": "uuid",
      "title": "Chicken Salad",
      "last_logged": "2026-03-15",
      "frequency": 3
    }
  ],
  "templates": [
    {
      "id": "uuid",
      "name": "Weekday Lunch",
      "meals": ["Sandwich", "Apple"]
    }
  ]
}
```
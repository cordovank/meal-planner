# API Contracts: Profile Management

**Context**: REST API endpoints for user profiles and nutrition targets

## Endpoints

### GET /api/v1/profiles
List user profiles.

**Response**: 200 OK
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Me",
      "calorie_target": 2000,
      "is_default": true,
      "targets": {
        "protein_g": {"target": 150, "tolerance": 15},
        "fat_g": {"target": 70, "tolerance": 7},
        "added_sugar_g": {"target": 25, "tolerance": 5}
      },
      "created_at": "2026-03-16T10:00:00Z"
    }
  ]
}
```

### POST /api/v1/profiles
Create a new profile.

**Request Body**:
```json
{
  "name": "Partner",
  "calorie_target": 1800,
  "targets": {
    "protein_g": {"target": 120, "tolerance": 12},
    "carbohydrates_g": {"target": 200, "tolerance": 20},
    "fat_g": {"target": 60, "tolerance": 6},
    "added_sugar_g": {"target": 20, "tolerance": 4}
  }
}
```

**Response**: 201 Created (profile object)

### GET /api/v1/profiles/{id}
Get profile details.

**Response**: 200 OK (profile object)

### PUT /api/v1/profiles/{id}
Update profile.

**Request Body**: Same as POST

**Response**: 200 OK (updated profile)

### DELETE /api/v1/profiles/{id}
Delete profile.

**Response**: 204 No Content

### POST /api/v1/profiles/{id}/compare
Compare recipe/meal against profile.

**Request Body**:
```json
{
  "recipe_id": "uuid",
  "portion_size": 1.0
}
```

**Response**: 200 OK
```json
{
  "profile_name": "Me",
  "fit": "within_range",
  "details": {
    "calories": {"actual": 450, "target": 500, "status": "approaching"},
    "protein_g": {"actual": 25, "target": 30, "status": "within_range"},
    "added_sugar_g": {"actual": 8, "target": 10, "status": "exceeding"}
  },
  "gaps": [
    {
      "nutrient": "protein_g",
      "short_by": 5,
      "suggestions": ["Add Greek yogurt (+15g protein)"]
    }
  ]
}
```
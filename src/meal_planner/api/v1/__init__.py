"""API v1 routers."""

from .food import router as food_router
from .profiles import router as profiles_router
from .recipes import router as recipes_router

__all__ = ["food_router", "profiles_router", "recipes_router"]
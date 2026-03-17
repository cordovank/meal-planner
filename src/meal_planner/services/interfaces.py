# ./src/meal_planner/services/interfaces.py

from __future__ import annotations

from typing import Generic, Iterable, Optional, Protocol, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class RepositoryProtocol(Protocol, Generic[T, ID]):
    """Protocol for repository actions used by services."""

    async def get(self, id: ID) -> Optional[T]:
        ...

    async def list(self, *, limit: int | None = None, offset: int | None = None) -> list[T]:
        ...

    async def add(self, obj: T) -> T:
        ...

    async def update(self, obj: T) -> T:
        ...

    async def delete(self, obj: T) -> None:
        ...


class SearchRepositoryProtocol(Protocol[T]):
    """Optional protocol for repositories that support searching."""

    async def search(self, query: str, limit: int = 10) -> list[T]:
        ...

from . import repositories as repo
from .models import Cinema
from typing import Any


def update_rating(cinema_id: int, new_value: float) -> Cinema:
    """Domain action: update ranking/rating for a cinema and return refreshed instance."""
    cinema = repo.get(cinema_id)
    cinema.update_rating(new_value)
    return cinema


def create(**data) -> Cinema:
    """Create and persist a new cinema."""
    return repo.create(**data)


def update(cinema_id: int, **data: Any) -> Cinema:
    """Update provided fields for an existing cinema and return the saved instance."""
    return repo.update(cinema_id, **data)


def delete(cinema_id: int) -> None:
    """Delete a cinema (silent if it does not exist)."""
    repo.delete(cinema_id)


def list_top(limit: int = 10):
    """Return top cinemas ordered by ranking descending limited by 'limit'."""
    return repo.list_top(limit)


def list_all(order: str = 'nomecinema'):
    """List all cinemas ordered by the specified field (defaults to Portuguese field name)."""
    return repo.list_all(order)


def get(cinema_id: int) -> Cinema:
    """Retrieve a single cinema by primary key."""
    return repo.get(cinema_id)


def search(term: str, limit: int | None = None):
    """Search cinemas by partial case-insensitive name match. Optional limit."""
    return repo.search(term, limit)

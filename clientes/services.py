from . import repositories as repo
from .models import Cliente
from typing import Any


def create(**data) -> Cliente:
    """Create and persist a new client."""
    return repo.create(**data)


def get(client_id: int) -> Cliente:
    """Retrieve a client by primary key."""
    return repo.get(client_id)


def search(name_fragment: str, limit: int | None = None):
    """Search clients by partial case-insensitive name match. Optional limit."""
    return repo.search(name_fragment, limit)


def list_all(order: str = 'nomecliente'):
    """List all clients ordered by the provided field (Portuguese default)."""
    return repo.list_all(order)


def update(client_id: int, **data: Any) -> Cliente:
    """Update provided fields of a client and return the persisted instance.
    Unspecified fields remain unchanged. Raises Cliente.DoesNotExist if not found.
    """
    return repo.update(client_id, **data)


def delete(client_id: int) -> None:
    """Delete client silently if it already does not exist."""
    repo.delete(client_id)

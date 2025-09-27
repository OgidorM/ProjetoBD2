from . import repositories as repo
from .models import Funcionario
from typing import Any


def create(**data) -> Funcionario:
    """Create and persist a new employee."""
    return repo.create(**data)


def get(employee_id: int) -> Funcionario:
    """Retrieve an employee by primary key."""
    return repo.get(employee_id)


def list_all(order: str = 'nomefuncionario'):
    """List all employees ordered by the provided field (Portuguese default)."""
    return repo.list_all(order)


def list_by_cinema(cinema_id: int):
    """List employees filtered by cinema id."""
    return repo.list_by_cinema(cinema_id)


def search(name_fragment: str, limit: int | None = None):
    """Search employees by partial case-insensitive name match. Optional limit."""
    return repo.search(name_fragment, limit)


def update(employee_id: int, **data: Any) -> Funcionario:
    """Update provided fields of an employee and return the persisted instance."""
    return repo.update(employee_id, **data)


def delete(employee_id: int) -> None:
    """Delete employee silently if it already does not exist."""
    repo.delete(employee_id)

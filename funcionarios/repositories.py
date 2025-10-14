from typing import Iterable, Optional, Any
from .models import Funcionario


def get(employee_id: int) -> Funcionario:
    return Funcionario.objects.get(pk=employee_id)


def list_all(order: str = 'nomefuncionario') -> Iterable[Funcionario]:
    return Funcionario.objects.all().order_by(order)


def list_by_cinema(cinema_id: int) -> Iterable[Funcionario]:
    return Funcionario.objects.filter(cinemaid_id=cinema_id).order_by('nomefuncionario')


def search(term: str, limit: Optional[int] = None) -> Iterable[Funcionario]:
    qs = Funcionario.objects.filter(nomefuncionario__icontains=term).order_by('nomefuncionario')
    return qs[:limit] if limit else qs


def delete(employee_id: int) -> None:
    Funcionario.objects.filter(pk=employee_id).delete()


def create(**data: Any) -> Funcionario:
    """Persist and return a new Funcionario instance."""
    return Funcionario.objects.create(**data)


def update(employee_id: int, **data: Any) -> Funcionario:
    """Update provided fields and return the saved Funcionario instance."""
    employee = get(employee_id)
    for field, value in data.items():
        setattr(employee, field, value)
    employee.save()
    return employee

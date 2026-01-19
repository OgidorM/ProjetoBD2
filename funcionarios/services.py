from typing import Any

from django.db import transaction

from bd2ap1.models import Vendas
from . import repositories as repo
from .models import Funcionario
from .models_auth import FuncionarioProfile


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


@transaction.atomic
def delete(employee_id: int) -> None:
    """Remove funcionário mantendo histórico financeiro.

    Regra:
      - Vendas não são apagadas; ficam com funcionarioid=NULL.
      - Se existir login associado (FuncionarioProfile), ele é removido.
    """
    # 1) Desvincula vendas
    Vendas.objects.filter(funcionarioid_id=employee_id).update(funcionarioid=None)

    # 2) Remove vínculo auth (FuncionarioProfile -> Funcionarios é PROTECT)
    profile = FuncionarioProfile.objects.select_related('user').filter(funcionario_dados_id=employee_id).first()
    if profile:
        user = profile.user
        profile.delete()
        if user:
            user.delete()

    # 3) Apaga o registro do funcionário
    repo.delete(employee_id)

from typing import Iterable, Optional
from .models import Funcionario


def get(funcionario_id: int) -> Funcionario:
    return Funcionario.objects.get(pk=funcionario_id)


def list_all(order: str = 'nomefuncionario') -> Iterable[Funcionario]:
    return Funcionario.objects.all().order_by(order)


def por_cinema(cinema_id: int) -> Iterable[Funcionario]:
    return Funcionario.objects.filter(cinemaid_id=cinema_id).order_by('nomefuncionario')


def search(term: str, limit: Optional[int] = None) -> Iterable[Funcionario]:
    qs = Funcionario.objects.filter(nomefuncionario__icontains=term).order_by('nomefuncionario')
    return qs[:limit] if limit else qs


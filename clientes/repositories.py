from typing import Iterable, Optional
from .models import Cliente


def get(cliente_id: int) -> Cliente:
    return Cliente.objects.get(pk=cliente_id)


def list_all(order: str = 'nomecliente') -> Iterable[Cliente]:
    return Cliente.objects.all().order_by(order)


def search(term: str, limit: Optional[int] = None) -> Iterable[Cliente]:
    qs = Cliente.objects.filter(nomecliente__icontains=term).order_by('nomecliente')
    return qs[:limit] if limit else qs


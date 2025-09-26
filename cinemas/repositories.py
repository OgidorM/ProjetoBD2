from typing import Iterable, Optional
from .models import Cinema

# Thin repository layer encapsulating ORM queries.

def get(cinema_id: int) -> Cinema:
    return Cinema.objects.get(pk=cinema_id)


def list_all(order: str = 'nomecinema') -> Iterable[Cinema]:
    return Cinema.objects.all().order_by(order)


def top(limit: int = 10) -> Iterable[Cinema]:
    return Cinema.objects.order_by('-ranking')[:limit]


def search(term: str, limit: Optional[int] = None) -> Iterable[Cinema]:
    qs = Cinema.objects.filter(nomecinema__icontains=term).order_by('nomecinema')
    return qs[:limit] if limit else qs


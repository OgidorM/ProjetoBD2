from typing import Iterable, Optional, Any
from .models import Cinema
from django.db.models import QuerySet


def get(cinema_id: int) -> Cinema:
    return Cinema.objects.get(pk=cinema_id)


def list_all(order: str = 'nomecinema') -> Iterable[Cinema]:
    return Cinema.objects.all().order_by(order)


def list_top(limit: int = 10) -> Iterable[Cinema]:
    return Cinema.objects.order_by('-ranking')[:limit]


def search(term: str, limit: Optional[int] = None) -> Iterable[Cinema]:
    qs: QuerySet[Cinema] = Cinema.objects.filter(nomecinema__icontains=term).order_by('nomecinema')
    return qs[:limit] if limit else qs


def delete(cinema_id: int) -> None:
    Cinema.objects.filter(pk=cinema_id).delete()


def create(**data: Any) -> Cinema:
    """Persist and return a new Cinema instance."""
    return Cinema.objects.create(**data)


def update(cinema_id: int, **data: Any) -> Cinema:
    """Update provided fields for a cinema and return the saved instance."""
    cinema = get(cinema_id)
    for field, value in data.items():
        setattr(cinema, field, value)
    cinema.save()
    return cinema

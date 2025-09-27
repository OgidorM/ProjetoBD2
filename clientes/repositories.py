from typing import Iterable, Optional, Any
from .models import Cliente
from django.db.models import QuerySet

# Repository layer (all method names in English)

def get(client_id: int) -> Cliente:
    return Cliente.objects.get(pk=client_id)


def list_all(order: str = 'nomecliente') -> Iterable[Cliente]:
    return Cliente.objects.all().order_by(order)


def search(term: str, limit: Optional[int] = None) -> Iterable[Cliente]:
    qs: QuerySet[Cliente] = Cliente.objects.filter(nomecliente__icontains=term).order_by('nomecliente')
    return qs[:limit] if limit else qs


def delete(client_id: int) -> None:
    Cliente.objects.filter(pk=client_id).delete()

# --- Added for service layer consistency ---

def create(**data: Any) -> Cliente:
    """Persist and return a new Cliente instance."""
    return Cliente.objects.create(**data)


def update(client_id: int, **data: Any) -> Cliente:
    """Update provided fields and return the saved Cliente instance."""
    client = get(client_id)
    for field, value in data.items():
        setattr(client, field, value)
    client.save()
    return client

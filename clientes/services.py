from . import repositories as repo
from .models import Cliente


def criar_cliente(**dados) -> Cliente:
    return Cliente.objects.create(**dados)


def obter(cliente_id: int) -> Cliente:
    return repo.get(cliente_id)


def pesquisar(nome_fragmento: str, limite: int | None = None):
    return repo.search(nome_fragmento, limite)


def listar():
    return repo.list_all()


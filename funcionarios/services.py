from . import repositories as repo
from .models import Funcionario


def contratar_funcionario(**dados) -> Funcionario:
    return Funcionario.objects.create(**dados)


def obter(funcionario_id: int) -> Funcionario:
    return repo.get(funcionario_id)


def listar():
    return repo.list_all()


def listar_por_cinema(cinema_id: int):
    return repo.por_cinema(cinema_id)


def pesquisar(nome_fragmento: str, limite: int | None = None):
    return repo.search(nome_fragmento, limite)


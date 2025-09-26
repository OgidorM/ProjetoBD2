from . import repositories as repo
from .models import Cinema


def atualizar_ranking(cinema_id: int, novo_valor: float) -> Cinema:
    cinema = repo.get(cinema_id)
    cinema.atualizar_ranking(novo_valor)
    return cinema


def criar_cinema(**dados) -> Cinema:
    # (Regra de negócio simples; pode validar mais tarde)
    cinema = Cinema.objects.create(**dados)
    return cinema


def listar_top(limit: int = 10):
    return repo.top(limit)


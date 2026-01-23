from typing import Optional, Iterable, Any
from django.contrib.auth.models import User
from django.db.models import QuerySet
from clientes.models import ClienteProfile
from bd2ap1.models import Clientes as TabelaClientes


class ClienteRepository:
    """
    Repositório Unificado: Auth + Admin.
    """

    #PARTE 1: Métodos de Autenticação
    def get_by_user(self, user: User) -> Optional[ClienteProfile]:
        try:
            return ClienteProfile.objects.select_related('cliente_dados').get(user=user)
        except ClienteProfile.DoesNotExist:
            return None

    def exists_by_username(self, username: str) -> bool:
        return User.objects.filter(username=username).exists()

    #PARTE 2: Métodos do Painel Admin

    def get_cliente_por_id(self, cliente_id: int) -> TabelaClientes:
        return TabelaClientes.objects.get(pk=cliente_id)

    def list_all(self, order_by: str = 'nomecliente') -> Iterable[TabelaClientes]:
        return TabelaClientes.objects.all().order_by(order_by)

    def search(self, term: str, limit: Optional[int] = None) -> Iterable[TabelaClientes]:
        qs = TabelaClientes.objects.filter(nomecliente__icontains=term).order_by('nomecliente')
        return qs[:limit] if limit else qs

    def delete(self, cliente_id: int) -> None:
        TabelaClientes.objects.filter(pk=cliente_id).delete()

    def update_dados(self, cliente_id: int, **data: Any) -> TabelaClientes:
        # Atualiza a tabela de dados pessoais
        cliente = self.get_cliente_por_id(cliente_id)
        for field, value in data.items():
            setattr(cliente, field, value)
        cliente.save()
        return cliente

    def create_dados(self, **data: Any) -> TabelaClientes:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("CALL inserir_cliente(%s, %s, %s, %s, %s, %s, %s, %s)", [
                data.get('nomecliente'),
                data.get('emailcliente'),
                data.get('telefonecliente'),
                data.get('datanascimento'),
                data.get('moradacliente'),
                data.get('codigopostalcliente'),
                data.get('localidadecliente'),
                data.get('nif')
            ])
        return TabelaClientes.objects.get(emailcliente=data.get('emailcliente'))

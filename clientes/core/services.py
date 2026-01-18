from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from bd2ap1.models import Vendas
from clientes.models import ClienteProfile
from clientes.data.repositories import ClienteRepository
from .dtos import NovoClienteDTO
from .exceptions import ClienteJaExisteException, ClienteServiceException


class ClienteService:

    def __init__(self):
        self.repository = ClienteRepository()

    #PARTE 1: Autenticação API

    @transaction.atomic
    def registrar_novo_cliente(self, dados: NovoClienteDTO) -> ClienteProfile:
        if self.repository.exists_by_username(dados.username):
            raise ClienteJaExisteException(f"O utilizador '{dados.username}' já existe.")

        try:
            user = User.objects.create_user(
                username=dados.username,
                email=dados.email,
                password=dados.password
            )

            # Usamos o repositório para criar os dados pessoais
            cliente_dados = self.repository.create_dados(
                nomecliente=dados.nome_completo,
                emailcliente=dados.email,
                telefonecliente=dados.telefone,
                nif=dados.nif,
                moradacliente=dados.morada,
                codigopostalcliente=dados.codigo_postal,
                localidadecliente=dados.localidade,
                datanascimento=dados.data_nascimento
            )

            # Criamos o perfil vinculando os dois
            profile = ClienteProfile.objects.create(
                user=user,
                cliente_dados=cliente_dados
            )
            return profile

        except IntegrityError as e:
            raise ClienteServiceException(f"Erro de integridade no banco: {str(e)}")
        except Exception as e:
            raise ClienteServiceException(f"Erro sistêmico ao registrar: {str(e)}")

    def get_cliente_por_user(self, user: User):
        return self.repository.get_by_user(user)

    #PARTE 2: Métodos para o Admin (Backoffice)

    def listar_todos(self):
        return self.repository.list_all()

    def buscar_por_id(self, cliente_id: int):
        return self.repository.get_cliente_por_id(cliente_id)

    def pesquisar(self, termo: str, limit: int = None):
        return self.repository.search(termo, limit)

    def criar_cliente_admin(self, data: dict):
        return self.repository.create_dados(**data)

    def atualizar_cliente(self, cliente_id: int, data: dict):
        return self.repository.update_dados(cliente_id, **data)

    @transaction.atomic
    def deletar_cliente(self, cliente_id: int):
        """
        Regra:
          - Vendas nunca são apagadas; ficam com clienteid=NULL.
          - Se existir login Django associado (ClienteProfile), ele é removido.
        """
        # 1) Desvincula vendas (mantém histórico financeiro)
        Vendas.objects.filter(clienteid_id=cliente_id).update(clienteid=None)

        # 2) Remove vínculo auth (ClienteProfile -> Clientes é PROTECT)
        profile = ClienteProfile.objects.select_related('user').filter(cliente_dados_id=cliente_id).first()
        if profile:
            user = profile.user
            profile.delete()
            # apaga também o user do Django
            if user:
                user.delete()

        # 3) Apaga o registro da tabela Clientes
        self.repository.delete(cliente_id)
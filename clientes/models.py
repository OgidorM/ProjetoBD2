# /home/driblades/Documents/BD2/b2da1/clientes/models.py
from django.db import models
from django.conf import settings
from bd2ap1.models import Clientes as TabelaClientesLegada


class ClienteProfile(models.Model):
    """
    Entidade de Vínculo (Link Table).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cliente_profile',
        verbose_name="Login do Sistema"
    )

    cliente_dados = models.OneToOneField(
        TabelaClientesLegada,
        on_delete=models.PROTECT,  # Se apagar o login, mantém o histórico de compras
        related_name='auth_profile',
        verbose_name="Dados do Cliente"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cliente_profiles'
        verbose_name = 'Perfil de Cliente'

    def __str__(self):
        return f"{self.user.username} -> {self.cliente_dados.nomecliente}"
from django.db import models
from django.conf import settings

from bd2ap1.models import Funcionarios as TabelaFuncionariosLegada


class FuncionarioProfile(models.Model):
    """Vínculo entre o login do Django (User) e um registro na tabela 'funcionarios'."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='funcionario_profile',
        verbose_name='Login do Sistema',
    )

    funcionario_dados = models.OneToOneField(
        TabelaFuncionariosLegada,
        on_delete=models.PROTECT,
        related_name='auth_profile',
        verbose_name='Dados do Funcionário',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'funcionario_profiles'
        verbose_name = 'Perfil de Funcionário'

    def __str__(self):
        return f"{self.user.username} -> {self.funcionario_dados.nomefuncionario}"


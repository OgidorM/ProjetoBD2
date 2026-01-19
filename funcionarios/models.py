from bd2ap1.models import Funcionarios as _Funcionarios

class Funcionario(_Funcionarios):
    """Proxy model for domain-level logic over funcionarios table."""
    class Meta:
        proxy = True
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'

    def nome_display(self):
        return self.nomefuncionario


# Modelo de vínculo Auth <-> Funcionários
from .models_auth import FuncionarioProfile

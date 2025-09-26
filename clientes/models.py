from bd2ap1.models import Clientes as _Clientes

class Cliente(_Clientes):
    """Proxy model for domain-level Cliente logic (uses existing 'clientes' table)."""
    class Meta:
        proxy = True
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def nome_display(self):
        return self.nomecliente or f"Cliente {self.clienteid}"


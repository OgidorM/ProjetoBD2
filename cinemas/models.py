from bd2ap1.models import Cinemas as _Cinemas

class Cinema(_Cinemas):
    """Proxy model providing a cleaner domain-facing singular name.
    Underlying table: cinemas (NO schema change / NO migration needed).
    """
    class Meta:
        proxy = True
        verbose_name = 'Cinema'
        verbose_name_plural = 'Cinemas'

    # Domain-specific helper methods can live here (kept minimal for now)
    def atualizar_ranking(self, novo_valor: float):
        # Clamp between 0 and 5 according to business rule
        self.ranking = max(0, min(5, novo_valor))
        self.save(update_fields=["ranking"])

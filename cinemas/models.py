from bd2ap1.models import Cinemas as _Cinemas

class Cinema(_Cinemas):
    """Proxy model providing a cleaner domain-facing singular name.
    Underlying table: cinemas (NO schema change / NO migration needed).
    """
    class Meta:
        proxy = True
        verbose_name = 'Cinema'
        verbose_name_plural = 'Cinemas'

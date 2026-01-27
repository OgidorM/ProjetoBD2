from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Avaliacoes

# Note: Ranking updates are now handled by database triggers (trg_atualizar_rankings_avaliacoes)
# to ensure data integrity and leverage DBMS logic as per DB2 project goals.



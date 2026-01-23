from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from django.db import connection
from .models import Avaliacoes, Filmes, Cinemas, Funcionarios, VendaLinhas

def call_db_function(func_name, *args):
    with connection.cursor() as cursor:
        # Construct the SQL query dynamically based on the number of arguments
        placeholders = ', '.join(['%s'] * len(args))
        sql = f"SELECT {func_name}({placeholders})"
        cursor.execute(sql, args)
        return cursor.fetchone()[0]

@receiver([post_save, post_delete], sender=Avaliacoes)
def update_rankings(sender, instance, **kwargs):
    # 1. Update Cinema Ranking
    # Since Avaliacao is linked to Venda, we find the cinema through the venda
    venda = instance.venda
    # We can get cinema from one of the tickets or the employee
    cinema = None
    if venda.funcionarioid and venda.funcionarioid.cinemaid:
        cinema = venda.funcionarioid.cinemaid
    else:
        # Try to find cinema from a ticket in this sale
        linha = venda.linhas.filter(bilheteid__isnull=False).first()
        if linha and linha.bilheteid.sessaoid.salaid.cinemaid:
            cinema = linha.bilheteid.sessaoid.salaid.cinemaid

    if cinema:
        avg_cinema = call_db_function('fn_calcular_media_avaliacao_cinema', cinema.cinemaid)
        cinema.ranking = float(avg_cinema)
        cinema.save()

    # 2. Update Employee Ranking
    if venda.funcionarioid:
        emp = venda.funcionarioid
        avg_emp = call_db_function('fn_calcular_media_avaliacao_funcionario', emp.funcionarioid)
        emp.ranking = float(avg_emp)
        emp.save()

    # 3. Update Movie Ranking(s)
    # A sale can have multiple movies. We update all movies involved in this sale.
    movies_in_sale = Filmes.objects.filter(sessoes__bilhetes__linhas_venda__vendaid=venda).distinct()
    for movie in movies_in_sale:
        avg_movie = call_db_function('fn_calcular_media_avaliacao_filme', movie.filmeid)
        movie.ranking = float(avg_movie)
        movie.save()



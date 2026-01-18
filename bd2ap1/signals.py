from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Avaliacoes, Filmes, Cinemas, Funcionarios, VendaLinhas

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
        avg_cinema = Avaliacoes.objects.filter(
            venda__linhas__bilheteid__sessaoid__salaid__cinemaid=cinema
        ).aggregate(Avg('avaliacaocinema'))['avaliacaocinema__avg'] or 0.0
        cinema.ranking = round(float(avg_cinema), 1)
        cinema.save()

    # 2. Update Employee Ranking
    if venda.funcionarioid:
        emp = venda.funcionarioid
        avg_emp = Avaliacoes.objects.filter(venda__funcionarioid=emp).aggregate(Avg('avaliacaofuncionario'))['avaliacaofuncionario__avg'] or 0.0
        emp.ranking = round(float(avg_emp), 1)
        emp.save()

    # 3. Update Movie Ranking(s)
    # A sale can have multiple movies. We update all movies involved in this sale.
    movies_in_sale = Filmes.objects.filter(sessoes__bilhetes__linhas_venda__vendaid=venda).distinct()
    for movie in movies_in_sale:
        avg_movie = Avaliacoes.objects.filter(
            venda__linhas__bilheteid__sessaoid__filmeid=movie
        ).aggregate(Avg('avaliacaofilme'))['avaliacaofilme__avg'] or 0.0
        movie.ranking = round(float(avg_movie), 1)
        movie.save()



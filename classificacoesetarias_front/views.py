from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.db import connection
from bd2ap1.models import ClassificacoesEtarias
from .forms import ClassificacaoEtariaForm

@login_required
def index(request):
    return redirect('lista_classificacoesetarias')

def lista_classificacoesetarias(request):
    classificacoes = ClassificacoesEtarias.objects.order_by('classificacaoid')
    return render(request, 'classificacoesetarias_front/lista_classificacoesetarias.html', {'classificacoes': classificacoes})

@login_required
def adicionar_classificacaoetaria(request):
    if request.method == 'POST':
        form = ClassificacaoEtariaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_classificacoesetarias')
    else:
        form = ClassificacaoEtariaForm()
    return render(request, 'classificacoesetarias_front/adicionar_classificacaoetaria.html', {'form': form})

def editar_classificacaoetaria(request, classificacaoid):
    classificacao = ClassificacoesEtarias.objects.get(classificacaoid=classificacaoid)
    if request.method == 'POST':
        form = ClassificacaoEtariaForm(request.POST, instance=classificacao)
        if form.is_valid():
            form.save()
            return redirect('lista_classificacoesetarias')
    else:
        form = ClassificacaoEtariaForm(instance=classificacao)
    return render(request, 'classificacoesetarias_front/editar_classificacaoetaria.html', {'form': form, 'classificacao': classificacao})

def remover_classificacaoetaria(request, classificacaoid):
    classificacao = ClassificacoesEtarias.objects.get(classificacaoid=classificacaoid)

    if request.method == 'POST':
        try:
            # Check for related objects before attempting deletion
            filmes_count = classificacao.filmes.count()

            if filmes_count > 0:
                error_msg = f"Não é possível remover esta classificação etária porque possui {filmes_count} filme(s) relacionado(s)."
                messages.error(request, error_msg)
                return render(request, 'classificacoesetarias_front/confirmar_delete_classificacaoetaria.html', {'classificacao': classificacao})

            # If no related objects, proceed with deletion
            classificacao.delete()

            # Reset the auto-increment sequence for PostgreSQL
            with connection.cursor() as cursor:
                cursor.execute("SELECT setval(pg_get_serial_sequence('classificacoesetarias', 'classificacaoid'), COALESCE((SELECT MAX(classificacaoid) FROM classificacoesetarias), 1), false);")

            messages.success(request, f'Classificação etária "{classificacao.nomeclassificacao}" foi removida com sucesso.')
            return redirect('lista_classificacoesetarias')

        except ProtectedError as e:
            messages.error(request, 'Não é possível remover esta classificação etária porque possui dados relacionados.')
            return render(request, 'classificacoesetarias_front/confirmar_delete_classificacaoetaria.html', {'classificacao': classificacao})

    # GET request - show confirmation page with related objects info
    filmes_count = classificacao.filmes.count()

    context = {
        'classificacao': classificacao,
        'filmes_count': filmes_count,
        'has_related_objects': filmes_count > 0
    }

    return render(request, 'classificacoesetarias_front/confirmar_delete_classificacaoetaria.html', context)

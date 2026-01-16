from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.db import connection
from bd2ap1.models import Vendas
from .forms import VendaForm


@login_required
def index(request):
    return redirect('lista_vendas')

@login_required
def lista_vendas(request):
    vendas = Vendas.objects.select_related('clienteid', 'funcionarioid').order_by('vendaid')
    return render(request, 'vendas_front/lista_vendas.html', {'vendas': vendas})

@login_required
def adicionar_venda(request):
    if request.method == 'POST':
        form = VendaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_vendas')
    else:
        form = VendaForm()
    return render(request, 'vendas_front/adicionar_venda.html', {'form': form})

def editar_venda(request, vendaid):
    venda = Vendas.objects.get(vendaid=vendaid)
    if request.method == 'POST':
        form = VendaForm(request.POST, instance=venda)
        if form.is_valid():
            form.save()
            return redirect('lista_vendas')
    else:
        form = VendaForm(instance=venda)
    return render(request, 'vendas_front/editar_venda.html', {'form': form, 'venda': venda})

def remover_venda(request, vendaid):
    venda = Vendas.objects.get(vendaid=vendaid)

    if request.method == 'POST':
        try:
            # Check for related objects before attempting deletion
            linhas_count = venda.linhas.count()
            avaliacao_exists = hasattr(venda, 'avaliacao')

            if linhas_count > 0 or avaliacao_exists:
                error_parts = []
                if linhas_count > 0:
                    error_parts.append(f"{linhas_count} linha(s) de venda")
                if avaliacao_exists:
                    error_parts.append("1 avaliação")
                
                error_msg = f"Não é possível remover esta venda porque possui dados relacionados: {', '.join(error_parts)}."
                messages.error(request, error_msg)
                return render(request, 'vendas_front/confirmar_delete_venda.html', {'venda': venda})

            # If no related objects, proceed with deletion
            venda.delete()

            # Reset the auto-increment sequence for PostgreSQL
            with connection.cursor() as cursor:
                cursor.execute("SELECT setval(pg_get_serial_sequence('vendas', 'vendaid'), COALESCE((SELECT MAX(vendaid) FROM vendas), 1), false);")

            messages.success(request, f'Venda #{venda.vendaid} foi removida com sucesso.')
            return redirect('lista_vendas')

        except ProtectedError as e:
            messages.error(request, 'Não é possível remover esta venda porque possui dados relacionados.')
            return render(request, 'vendas_front/confirmar_delete_venda.html', {'venda': venda})

    # GET request - show confirmation page with related objects info
    linhas_count = venda.linhas.count()
    avaliacao_exists = hasattr(venda, 'avaliacao')

    context = {
        'venda': venda,
        'linhas_count': linhas_count,
        'avaliacao_exists': avaliacao_exists,
        'has_related_objects': linhas_count > 0 or avaliacao_exists
    }

    return render(request, 'vendas_front/confirmar_delete_venda.html', context)
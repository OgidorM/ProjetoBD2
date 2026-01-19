from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.db import connection
from django.http import Http404
from django.utils.dateparse import parse_date

from bd2ap1.models import Vendas
from .forms import VendaForm
from .reports.detailed_sales_report import build_detailed_sales_csv_response


def eh_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(eh_admin)
def index(request):
    return redirect('lista_vendas')

@user_passes_test(eh_admin)
def lista_vendas(request):
    vendas = Vendas.objects.select_related('clienteid', 'funcionarioid').order_by('vendaid')
    return render(request, 'vendas_front/lista_vendas.html', {'vendas': vendas})

@user_passes_test(eh_admin)
def adicionar_venda(request):
    if request.method == 'POST':
        form = VendaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_vendas')
    else:
        form = VendaForm()
    return render(request, 'vendas_front/adicionar_venda.html', {'form': form})

@user_passes_test(eh_admin)
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

@user_passes_test(eh_admin)
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

@user_passes_test(eh_admin)
def export_mv_vendas_diarias_csv(request):
    """
    Exporta relatótio detalhado de vendas.
    Substitui a antiga exportação da MV para fornecer dados granulares.
    """

    start_raw = request.GET.get('start')
    end_raw = request.GET.get('end')

    start = parse_date(start_raw) if start_raw else None
    end = parse_date(end_raw) if end_raw else None

    # Se o usuário passou valor inválido, falha de forma explícita
    if start_raw and start is None:
        raise Http404("Parâmetro 'start' inválido. Use YYYY-MM-DD.")
    if end_raw and end is None:
        raise Http404("Parâmetro 'end' inválido. Use YYYY-MM-DD.")

    try:
        return build_detailed_sales_csv_response(start=start, end=end)
    except Exception as exc:
        # Em caso de erro na query SQL
        raise Http404("Erro ao gerar relatório detalhado.") from exc
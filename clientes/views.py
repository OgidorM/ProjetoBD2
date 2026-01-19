from bd2ap1.mongo_logger import log_action
from django.http import HttpRequest, JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ProtectedError
from django.contrib.auth.decorators import user_passes_test

from clientes.core.services import ClienteService
from .forms import ClienteForm

# Instância global do serviço para usar nas views (padrão Controller)
service = ClienteService()

def eh_admin(user):
    """Verifica se o usuário é funcionário ou superusuário."""
    return user.is_staff or user.is_superuser


def _get_or_404(client_id: int):
    try:
        return service.buscar_por_id(client_id)
    except ObjectDoesNotExist:
        raise Http404("Client not found")


@user_passes_test(eh_admin)
def client_list(request: HttpRequest) -> HttpResponse:
    clients = service.listar_todos()
    if request.GET.get('format') == 'json':
        data = [{'id': c.clienteid, 'name': c.nomecliente, 'email': c.emailcliente, 'city': c.localidadecliente} for c
                in clients]
        return JsonResponse({'results': data})
    return render(request, 'clientes/list.html', {'clients': clients})


@user_passes_test(eh_admin)
def client_detail(request: HttpRequest, client_id: int) -> HttpResponse:
    client = _get_or_404(client_id)
    if request.GET.get('format') == 'json':
        return JsonResponse({
            'id': client.clienteid, 'name': client.nomecliente,
            'email': client.emailcliente, 'nif': client.nif
        })
    return render(request, 'clientes/detail.html', {'client': client})


@user_passes_test(eh_admin)
def client_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            client = service.criar_cliente_admin(form.cleaned_data)

            log_action(user=request.user, action='CREATE', target_model='Cliente', target_id=client.clienteid,
                       details={'nome': client.nomecliente})
            return redirect(reverse('clientes:detail', args=[client.clienteid]))
    else:
        form = ClienteForm()
    return render(request, 'clientes/form.html', {'form': form, 'mode': 'create'})


@user_passes_test(eh_admin)
def client_update(request: HttpRequest, client_id: int) -> HttpResponse:
    client = _get_or_404(client_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=client)
        if form.is_valid():
            old_name = client.nomecliente

            service.atualizar_cliente(client_id, form.cleaned_data)

            log_action(user=request.user, action='UPDATE', target_model='Cliente', target_id=client_id,
                       details={'from': old_name})
            return redirect(reverse('clientes:detail', args=[client_id]))
    else:
        form = ClienteForm(instance=client)
    return render(request, 'clientes/form.html', {'form': form, 'mode': 'update', 'client': client})


@user_passes_test(eh_admin)
def client_delete(request: HttpRequest, client_id: int) -> HttpResponse:
    client = _get_or_404(client_id)
    related_vendas = client.vendas.all()

    if request.method == 'POST':
        try:
            client_name = client.nomecliente
            service.deletar_cliente(client_id)

            log_action(user=request.user, action='DELETE', target_model='Cliente', target_id=client_id,
                       details={'nome': client_name})
            messages.success(request, "Cliente eliminado.")
            return redirect(reverse('clientes:list'))
        except ProtectedError:
            messages.error(request, "Não é possível eliminar devido a vendas associadas.")
            return render(request, 'clientes/confirm_delete.html', {'client': client, 'has_related_objects': True})

    return render(request, 'clientes/confirm_delete.html',
                  {'client': client, 'related_vendas': related_vendas, 'has_related_objects': related_vendas.exists()})


@user_passes_test(eh_admin)
def client_search(request: HttpRequest) -> HttpResponse:
    term = request.GET.get('q', '').strip()
    limit = request.GET.get('limit')
    limit = int(limit) if limit and limit.isdigit() else None

    results = service.pesquisar(term, limit) if term else []

    data = [{'id': c.clienteid, 'name': c.nomecliente} for c in results]
    return JsonResponse({'query': term, 'count': len(data), 'results': data})

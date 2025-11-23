from __future__ import annotations
from typing import Any, List, Dict

from django.contrib.auth.decorators import login_required
from bd2ap1.mongo_logger import log_action

from django.http import HttpRequest, JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from django.contrib import messages

from . import services
from .forms import ClienteForm
from .models import Cliente


def _get_or_404(client_id: int) -> Cliente:
    try:
        return services.get(client_id)
    except ObjectDoesNotExist as exc:
        raise Http404("Client not found") from exc


@login_required
def client_list(request: HttpRequest) -> HttpResponse:
    clients = services.list_all()
    if request.GET.get('format') == 'json':
        data: List[Dict[str, Any]] = [
            {
                'id': c.clienteid,
                'name': c.nomecliente,
                'email': c.emailcliente,
                'city': c.localidadecliente,
            }
            for c in clients
        ]
        return JsonResponse({'results': data})
    return render(request, 'clientes/list.html', {'clients': clients})


@login_required
def client_detail(request: HttpRequest, client_id: int) -> HttpResponse:
    client = _get_or_404(client_id)
    if request.GET.get('format') == 'json':
        data = {
            'id': client.clienteid,
            'name': client.nomecliente,
            'email': client.emailcliente,
            'phone': client.telefonecliente,
            'city': client.localidadecliente,
            'nif': client.nif,
        }
        return JsonResponse(data)
    return render(request, 'clientes/detail.html', {'client': client})


@login_required
def client_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            client = services.create(**form.cleaned_data)

            log_action(
                user=request.user,
                action='CREATE',
                target_model='Cliente',
                target_id=client.clienteid,
                details={'nome': client.nomecliente, 'nif': client.nif}
            )

            return redirect(reverse('clientes:detail', args=[client.clienteid]))
    else:
        form = ClienteForm()
    return render(request, 'clientes/form.html', {'form': form, 'mode': 'create'})


@login_required
def client_update(request: HttpRequest, client_id: int) -> HttpResponse:
    client = _get_or_404(client_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=client)
        if form.is_valid():
            old_name = client.nomecliente

            services.update(client_id, **form.cleaned_data)

            log_action(
                user=request.user,
                action='UPDATE',
                target_model='Cliente',
                target_id=client_id,
                details={'changed_from': old_name, 'changed_to': client.nomecliente}
            )


            return redirect(reverse('clientes:detail', args=[client_id]))
    else:
        form = ClienteForm(initial={
            'nomecliente': client.nomecliente,
            'emailcliente': client.emailcliente,
            'telefonecliente': client.telefonecliente,
            'datanascimento': client.datanascimento,
            'moradacliente': client.moradacliente,
            'codigopostalcliente': client.codigopostalcliente,
            'localidadecliente': client.localidadecliente,
            'nif': client.nif,
        })
    return render(request, 'clientes/form.html', {'form': form, 'mode': 'update', 'client': client})


@login_required
def client_delete(request: HttpRequest, client_id: int) -> HttpResponse:
    client = _get_or_404(client_id)

    related_vendas = client.vendas.all()

    if request.method == 'POST':
        try:
            client_name = client.nomecliente

            services.delete(client_id)

            log_action(
                user=request.user,
                action='DELETE',
                target_model='Cliente',
                target_id=client_id,
                details={'nome_apagado': client_name, 'tipo': 'SET_NULL_VENDAS'}
            )

            messages.success(request,
                             f"Cliente '{client_name or f'Cliente {client.clienteid}'}' eliminado. O histórico de vendas foi mantido (anónimo).")
            return redirect(reverse('clientes:list'))

        except ProtectedError as e:
            msg_debug = f"[ERRO-VIEW-CLIENTE] O banco de dados bloqueou! Objetos protegidos: {e.protected_objects}"
            messages.error(request, msg_debug)
            messages.error(request, f"Não é possível eliminar o cliente devido a restrições de integridade.")
            return render(request, 'clientes/confirm_delete.html', {
                'client': client,
                'has_related_objects': True
            })

    has_related = related_vendas.exists()

    return render(request, 'clientes/confirm_delete.html', {
        'client': client,
        'related_vendas': related_vendas,
        'has_related_objects': has_related
    })


@login_required
def client_search(request: HttpRequest) -> HttpResponse:
    term = request.GET.get('q', '').strip()
    limit_raw = request.GET.get('limit')
    limit = int(limit_raw) if limit_raw and limit_raw.isdigit() else None
    results = services.search(term, limit) if term else []
    data = [
        {'id': c.clienteid, 'name': c.nomecliente}
        for c in results
    ]
    return JsonResponse({'query': term, 'count': len(data), 'results': data})
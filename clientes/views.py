from __future__ import annotations
from typing import Any, List, Dict
from django.http import HttpRequest, JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from . import services
from .forms import ClienteForm
from .models import Cliente


def _get_or_404(client_id: int) -> Cliente:
    try:
        return services.get(client_id)
    except ObjectDoesNotExist as exc:
        raise Http404("Client not found") from exc


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


def client_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            client = services.create(**form.cleaned_data)
            return redirect(reverse('clientes:detail', args=[client.clienteid]))
    else:
        form = ClienteForm()
    return render(request, 'clientes/form.html', {'form': form, 'mode': 'create'})


def client_update(request: HttpRequest, client_id: int) -> HttpResponse:
    client = _get_or_404(client_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            services.update(client_id, **form.cleaned_data)
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


def client_delete(request: HttpRequest, client_id: int) -> HttpResponse:
    client = _get_or_404(client_id)
    if request.method == 'POST':
        services.delete(client_id)
        return redirect(reverse('clientes:list'))
    return render(request, 'clientes/confirm_delete.html', {'client': client})


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


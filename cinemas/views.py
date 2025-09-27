from __future__ import annotations
from typing import Any, List, Dict
from django.http import HttpRequest, JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from . import services
from .forms import CinemaForm
from .models import Cinema

# Helper -----------------------------------------------------------------

def _get_or_404(cinema_id: int) -> Cinema:
    try:
        return services.get(cinema_id)
    except ObjectDoesNotExist as exc:
        raise Http404("Cinema not found") from exc


def cinema_list(request: HttpRequest) -> HttpResponse:
    cinemas = services.list_all()
    if request.GET.get('format') == 'json':
        data: List[Dict[str, Any]] = [
            {
                'id': c.cinemaid,
                'name': c.nomecinema,
                'ranking': float(c.ranking),
                'city': c.localidadecinema,
            }
            for c in cinemas
        ]
        return JsonResponse({'results': data})
    return render(request, 'cinemas/list.html', {'cinemas': cinemas})


def cinema_detail(request: HttpRequest, cinema_id: int) -> HttpResponse:
    cinema = _get_or_404(cinema_id)
    if request.GET.get('format') == 'json':
        data = {
            'id': cinema.cinemaid,
            'name': cinema.nomecinema,
            'ranking': float(cinema.ranking),
            'email': cinema.emailcinema,
            'phone': cinema.telefonecinema,
            'address': cinema.moradacinema,
            'postal_code': cinema.codigopostalcinema,
            'city': cinema.localidadecinema,
        }
        return JsonResponse(data)
    return render(request, 'cinemas/detail.html', {'cinema': cinema})


def cinema_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = CinemaForm(request.POST)
        if form.is_valid():
            cinema = services.create(**form.cleaned_data)
            return redirect(reverse('cinemas:detail', args=[cinema.cinemaid]))
    else:
        form = CinemaForm()
    return render(request, 'cinemas/form.html', {'form': form, 'mode': 'create'})


def cinema_update(request: HttpRequest, cinema_id: int) -> HttpResponse:
    cinema = _get_or_404(cinema_id)
    if request.method == 'POST':
        form = CinemaForm(request.POST)
        if form.is_valid():
            services.update(cinema_id, **form.cleaned_data)
            return redirect(reverse('cinemas:detail', args=[cinema_id]))
    else:
        # We pass initial data instead of binding instance.save() to keep business logic in services
        form = CinemaForm(initial={
            'nomecinema': cinema.nomecinema,
            'emailcinema': cinema.emailcinema,
            'telefonecinema': cinema.telefonecinema,
            'moradacinema': cinema.moradacinema,
            'codigopostalcinema': cinema.codigopostalcinema,
            'localidadecinema': cinema.localidadecinema,
            'ranking': cinema.ranking,
        })
    return render(request, 'cinemas/form.html', {'form': form, 'mode': 'update', 'cinema': cinema})


def cinema_delete(request: HttpRequest, cinema_id: int) -> HttpResponse:
    cinema = _get_or_404(cinema_id)
    if request.method == 'POST':
        # No business logic here beyond calling service
        services.delete(cinema_id)
        return redirect(reverse('cinemas:list'))
    return render(request, 'cinemas/confirm_delete.html', {'cinema': cinema})


def cinema_search(request: HttpRequest) -> HttpResponse:
    term = request.GET.get('q', '').strip()
    limit_raw = request.GET.get('limit')
    limit = int(limit_raw) if limit_raw and limit_raw.isdigit() else None
    results = services.search(term, limit) if term else []
    data = [
        {'id': c.cinemaid, 'name': c.nomecinema, 'ranking': float(c.ranking)}
        for c in results
    ]
    return JsonResponse({'query': term, 'count': len(data), 'results': data})


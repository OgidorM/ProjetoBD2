from __future__ import annotations
from typing import Any, List, Dict

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from django.contrib import messages

from bd2ap1.mongo_logger import log_action
from . import services
from .forms import CinemaForm
from .models import Cinema

# Helper -----------------------------------------------------------------

def _get_or_404(cinema_id: int) -> Cinema:
    try:
        return services.get(cinema_id)
    except ObjectDoesNotExist as exc:
        raise Http404("Cinema not found") from exc


@login_required
def cinema_list(request: HttpRequest) -> HttpResponse:
    cinemas = services.list_all()
    if request.GET.get('format') == 'json':
        data: List[Dict[str, Any]] = [
            {
                'id': c.cinemaid,
                'name': c.nomecinema,
                'ranking': float(c.ranking or 0),
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
            'ranking': float(cinema.ranking or 0),
            'email': cinema.emailcinema,
            'phone': cinema.telefonecinema,
            'address': cinema.moradacinema,
            'postal_code': cinema.codigopostalcinema,
            'city': cinema.localidadecinema,
        }
        return JsonResponse(data)
    return render(request, 'cinemas/detail.html', {'cinema': cinema})

@login_required()
def cinema_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = CinemaForm(request.POST)
        if form.is_valid():
            cinema = services.create(**form.cleaned_data)
            log_action(
                user=request.user,
                action='CREATE',
                target_model='Cinema',
                target_id=cinema.cinemaid,
                details={'nome': cinema.nomecinema, 'city': cinema.localidadecinema}
            )
            # ---------------------------------------
            return redirect(reverse('cinemas:detail', args=[cinema.cinemaid]))
    else:
        form = CinemaForm()
    return render(request, 'cinemas/form.html', {'form': form, 'mode': 'create'})

@login_required()
def cinema_update(request: HttpRequest, cinema_id: int) -> HttpResponse:
    cinema = _get_or_404(cinema_id)
    if request.method == 'POST':
        form = CinemaForm(request.POST, instance=cinema)
        if form.is_valid():
            old_name = cinema.nomecinema
            services.update(cinema_id, **form.cleaned_data)
            log_action(
                user=request.user,
                action='UPDATE',
                target_model='Cinema',
                target_id=cinema_id,
                details={'changed_from': old_name, 'changed_to': form.cleaned_data['nomecinema']}
            )

            return redirect(reverse('cinemas:detail', args=[cinema_id]))
    else:
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

@login_required()
def cinema_delete(request: HttpRequest, cinema_id: int) -> HttpResponse:
    cinema = _get_or_404(cinema_id)

    related_filmes = cinema.filmes.all()
    related_salas = cinema.salas.all()

    if request.method == 'POST':
        try:
            cinema_nome = cinema.nomecinema
            # Tenta apagar. O DB com Cascade leva tudo o resto.
            services.delete(cinema_id)
            log_action(
                user=request.user,
                action='DELETE',
                target_model='Cinema',
                target_id=cinema_id,
                details={'nome_apagado': cinema_nome, 'tipo': 'CASCADE_DELETE'}
            )

            messages.success(request,
             f"Cinema '{cinema.nomecinema}' e toda a sua infraestrutura (salas/filmes) foram eliminados.")
            return redirect(reverse('cinemas:list'))

        except ProtectedError as e:
            # Se cair aqui, é porque algo na BD (não visto nas migrations) bloqueou
            msg_debug = f"[ERRO-VIEW-CINEMA] O banco de dados bloqueou! Objetos protegidos: {e.protected_objects}"
            messages.error(request, msg_debug)
            messages.error(request, f"Não é possível eliminar o cinema '{cinema.nomecinema}' devido a um erro de integridade.")
            return render(request, 'cinemas/confirm_delete.html', {
                'cinema': cinema,
                'has_related_objects': True
            })

    has_related = related_filmes.exists() or related_salas.exists()

    return render(request, 'cinemas/confirm_delete.html', {
        'cinema': cinema,
        'related_filmes': related_filmes,
        'related_salas': related_salas,
        'has_related_objects': has_related
    })


def cinema_search(request: HttpRequest) -> HttpResponse:
    term = request.GET.get('q', '').strip()
    limit_raw = request.GET.get('limit')
    limit = int(limit_raw) if limit_raw and limit_raw.isdigit() else None
    results = services.search(term, limit) if term else []
    data = [
        {'id': c.cinemaid, 'name': c.nomecinema, 'ranking': float(c.ranking or 0)}
        for c in results
    ]
    return JsonResponse({'query': term, 'count': len(data), 'results': data})
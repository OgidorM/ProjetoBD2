from __future__ import annotations
from typing import Any, List, Dict
from django.http import HttpRequest, JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from django.contrib import messages

from . import services
from .forms import FuncionarioForm
from .models import Funcionario


def _get_or_404(employee_id: int) -> Funcionario:
    try:
        return services.get(employee_id)
    except ObjectDoesNotExist as exc:
        raise Http404("Employee not found") from exc


def employee_list(request: HttpRequest) -> HttpResponse:
    employees = services.list_all()
    if request.GET.get('format') == 'json':
        data: List[Dict[str, Any]] = [
            {
                'id': e.funcionarioid,
                'name': e.nomefuncionario,
                'role': e.cargo,
                'cinema_id': e.cinemaid_id,
                'ranking': float(e.ranking),
            }
            for e in employees
        ]
        return JsonResponse({'results': data})
    return render(request, 'funcionarios/list.html', {'employees': employees})


def employee_detail(request: HttpRequest, employee_id: int) -> HttpResponse:
    employee = _get_or_404(employee_id)
    if request.GET.get('format') == 'json':
        data = {
            'id': employee.funcionarioid,
            'name': employee.nomefuncionario,
            'email': employee.emailfuncionario,
            'phone': employee.telefonefuncionario,
            'role': employee.cargo,
            'cinema_id': employee.cinemaid_id,
            'admission': employee.admissao.isoformat() if employee.admissao else None,
            'salary': float(employee.salario),
            'ranking': float(employee.ranking),
        }
        return JsonResponse(data)
    return render(request, 'funcionarios/detail.html', {'employee': employee})


def employee_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            employee = services.create(**form.cleaned_data)
            return redirect(reverse('funcionarios:detail', args=[employee.funcionarioid]))
    else:
        form = FuncionarioForm()
    return render(request, 'funcionarios/form.html', {'form': form, 'mode': 'create'})


def employee_update(request: HttpRequest, employee_id: int) -> HttpResponse:
    employee = _get_or_404(employee_id)
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            services.update(employee_id, **form.cleaned_data)
            return redirect(reverse('funcionarios:detail', args=[employee_id]))
    else:
        form = FuncionarioForm(initial={
            'cinemaid': employee.cinemaid_id,
            'nomefuncionario': employee.nomefuncionario,
            'emailfuncionario': employee.emailfuncionario,
            'telefonefuncionario': employee.telefonefuncionario,
            'cargo': employee.cargo,
            'admissao': employee.admissao,
            'salario': employee.salario,
            'ranking': employee.ranking,
        })
    return render(request, 'funcionarios/form.html', {'form': form, 'mode': 'update', 'employee': employee})


def employee_delete(request: HttpRequest, employee_id: int) -> HttpResponse:
    employee = _get_or_404(employee_id)

    if request.method == 'POST':
        try:
            # Check for related objects before attempting deletion
            related_vendas = employee.vendas.all()

            if related_vendas.exists():
                # Build error message with related objects
                vendas_count = related_vendas.count()
                error_message = f"Não é possível eliminar o funcionário '{employee.nomefuncionario or f'Funcionário {employee.funcionarioid}'}' porque tem {vendas_count} venda{'s' if vendas_count > 1 else ''} associada{'s' if vendas_count > 1 else ''}. Elimine primeiro as vendas relacionadas."
                messages.error(request, error_message)
                return render(request, 'funcionarios/confirm_delete.html', {
                    'employee': employee,
                    'related_vendas': related_vendas,
                    'has_related_objects': True
                })

            # If no related objects, proceed with deletion
            services.delete(employee_id)
            messages.success(request, f"Funcionário '{employee.nomefuncionario or f'Funcionário {employee.funcionarioid}'}' foi eliminado com sucesso.")
            return redirect(reverse('funcionarios:list'))

        except ProtectedError as e:
            # Fallback error handling in case the service doesn't catch it
            messages.error(request, f"Não é possível eliminar o funcionário '{employee.nomefuncionario or f'Funcionário {employee.funcionarioid}'}' porque tem objetos relacionados.")
            return render(request, 'funcionarios/confirm_delete.html', {
                'employee': employee,
                'has_related_objects': True
            })

    # For GET requests, check if there are related objects to show warning
    related_vendas = employee.vendas.all()
    has_related = related_vendas.exists()

    return render(request, 'funcionarios/confirm_delete.html', {
        'employee': employee,
        'related_vendas': related_vendas,
        'has_related_objects': has_related
    })


def employee_search(request: HttpRequest) -> HttpResponse:
    term = request.GET.get('q', '').strip()
    limit_raw = request.GET.get('limit')
    limit = int(limit_raw) if limit_raw and limit_raw.isdigit() else None
    results = services.search(term, limit) if term else []
    data = [
        {'id': e.funcionarioid, 'name': e.nomefuncionario, 'role': e.cargo}
        for e in results
    ]
    return JsonResponse({'query': term, 'count': len(data), 'results': data})

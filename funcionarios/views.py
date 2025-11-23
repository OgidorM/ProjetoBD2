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
                # CORREÇÃO: Proteção contra ranking None
                'ranking': float(e.ranking or 0),
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
            # CORREÇÃO: Proteção contra ranking None
            'ranking': float(employee.ranking or 0),
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
        # CORREÇÃO CRÍTICA: Adicionado instance=employee
        form = FuncionarioForm(request.POST, instance=employee)
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

    related_vendas = employee.vendas.all()

    if request.method == 'POST':
        try:
            #Não precisa de bloqueio aqui, os models ja tem a lógica necessária
            services.delete(employee_id)

            emp_name = employee.nomefuncionario or f'Funcionário {employee.funcionarioid}'
            messages.success(request,
                             f"Funcionário '{emp_name}' eliminado. As vendas realizadas por ele foram mantidas (sem autor).")
            return redirect(reverse('funcionarios:list'))

        except ProtectedError as e:
            msg_debug = f"[ERRO-VIEW-FUNCIONARIO] O banco de dados bloqueou! Objetos protegidos: {e.protected_objects}"
            messages.error(request, msg_debug)
            messages.error(request, f"Não é possível eliminar o funcionário devido a restrições de integridade.")
            return render(request, 'funcionarios/confirm_delete.html', {
                'employee': employee,
                'has_related_objects': True
            })

    # Para o GET, verificamos se há vendas para mostrar o alerta
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
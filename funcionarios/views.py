from __future__ import annotations
from typing import Any, List, Dict

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpRequest, JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from django.contrib import messages

from bd2ap1.mongo_logger import log_action
from . import services
from .forms import FuncionarioForm
from .models import Funcionario
from .models_auth import FuncionarioProfile


def eh_admin(user):
    """Verifica se o usuário é funcionário (staff) ou superusuário."""
    return user.is_staff or user.is_superuser


def _get_or_404(employee_id: int) -> Funcionario:
    try:
        return services.get(employee_id)
    except ObjectDoesNotExist as exc:
        raise Http404("Employee not found") from exc


@user_passes_test(eh_admin)
def employee_list(request: HttpRequest) -> HttpResponse:
    employees = services.list_all()
    if request.GET.get('format') == 'json':
        data: List[Dict[str, Any]] = [
            {
                'id': e.funcionarioid,
                'name': e.nomefuncionario,
                'role': e.cargo,
                'cinema_id': e.cinemaid_id,
                'ranking': float(e.ranking or 0),
            }
            for e in employees
        ]
        return JsonResponse({'results': data})
    return render(request, 'funcionarios/list.html', {'employees': employees})


@user_passes_test(eh_admin)
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
            'ranking': float(employee.ranking or 0),
        }
        return JsonResponse(data)
    return render(request, 'funcionarios/detail.html', {'employee': employee})


@user_passes_test(eh_admin)
def employee_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            if not username or not password:
                form.add_error('username', 'Username é obrigatório.')
                form.add_error('password', 'Password é obrigatória.')
            else:
                # cria funcionário
                employee_data = {k: v for k, v in form.cleaned_data.items() if k not in ('username', 'password')}
                employee = services.create(**employee_data)

                # cria user staff para login do funcionário
                user = User.objects.create_user(username=username, email=employee.emailfuncionario or '', password=password)
                user.is_staff = True
                user.save()

                FuncionarioProfile.objects.create(user=user, funcionario_dados=employee)

                log_action(
                    user=request.user,
                    action='CREATE',
                    target_model='Funcionario',
                    target_id=employee.funcionarioid,
                    details={'nome': employee.nomefuncionario, 'cargo': employee.cargo, 'username': username}
                )

                return redirect(reverse('funcionarios:detail', args=[employee.funcionarioid]))
    else:
        form = FuncionarioForm()
    return render(request, 'funcionarios/form.html', {'form': form, 'mode': 'create'})


@user_passes_test(eh_admin)
def employee_update(request: HttpRequest, employee_id: int) -> HttpResponse:
    employee = _get_or_404(employee_id)
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, instance=employee)
        if form.is_valid():
            old_name = employee.nomefuncionario
            services.update(employee_id, **form.cleaned_data)

            log_action(
                user=request.user,
                action='UPDATE',
                target_model='Funcionario',
                target_id=employee_id,
                details={'changed_from': old_name, 'changed_to': employee.nomefuncionario}
            )

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


@user_passes_test(eh_admin)
def employee_delete(request: HttpRequest, employee_id: int) -> HttpResponse:
    """
    Remove o funcionário mas MANTÉM as vendas (campo 'funcionarioid' fica NULL).
    Garante a integridade dos relatórios de vendas por cinema.
    """
    employee = _get_or_404(employee_id)
    related_vendas = employee.vendas.all()

    if request.method == 'POST':
        try:
            emp_name = employee.nomefuncionario

            services.delete(employee_id)

            log_action(
                user=request.user,
                action='DELETE',
                target_model='Funcionario',
                target_id=employee_id,
                details={'nome_apagado': emp_name, 'tipo': 'SET_NULL_VENDAS'}
            )

            messages.success(request, f"Funcionário '{emp_name}' eliminado. Vendas mantidas sem autor.")
            return redirect(reverse('funcionarios:list'))

        except ProtectedError as e:
            msg_debug = f"[ERRO-VIEW-FUNCIONARIO] Bloqueio de integridade DB: {e.protected_objects}"
            messages.error(request, msg_debug)
            messages.error(request, "Não é possível eliminar o funcionário devido a restrições de integridade.")
            return render(request, 'funcionarios/confirm_delete.html', {
                'employee': employee,
                'has_related_objects': True
            })

    has_related = related_vendas.exists()

    return render(request, 'funcionarios/confirm_delete.html', {
        'employee': employee,
        'related_vendas': related_vendas,
        'has_related_objects': has_related
    })


@user_passes_test(eh_admin)
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
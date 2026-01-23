from datetime import datetime, date
from django.contrib.auth.decorators import user_passes_test

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.db import connection
from bd2ap1.models import Sessoes
from .forms import SessaoForm


def index(request):
    return redirect('lista_sessoes')


def lista_sessoes(request):
    sessoes = Sessoes.objects.select_related('filmeid', 'salaid').order_by('sessaoid')
    
    # Calculate occupation for each session
    # Note: Ideally this should be done via annotation or in bulk, but we are mandated to use the specific function
    for s in sessoes:
        with connection.cursor() as cursor:
            cursor.execute("SELECT fn_verificar_capacidade_sessao(%s)", [s.sessaoid])
            result = cursor.fetchone()
            s.ocupacao = result[0] if result else 0

    return render(request, 'sessoes_front/lista_sessoes.html', {'sessoes': sessoes})


def eh_admin(user):
    return user.is_staff or user.is_superuser


@user_passes_test(eh_admin)
def adicionar_sessao(request):
    if request.method == 'POST':
        form = SessaoForm(request.POST)
        if form.is_valid():
            # Get the cleaned data
            data = form.cleaned_data
            
            # Construct full datetime
            inicio_dt = datetime.combine(date.today(), data['inicio'])
            fim_dt = datetime.combine(date.today(), data['fim'])

            with connection.cursor() as cursor:
                cursor.execute("CALL inserir_sessao(%s, %s, %s, %s, %s, %s, %s)", [
                    data['salaid'].salaid if data['salaid'] else None,
                    data['filmeid'].filmeid if data['filmeid'] else None,
                    inicio_dt,
                    fim_dt,
                    data['versao'],
                    data['estadosessao'],
                    data['precosessao']
                ])

            messages.success(request, 'Sessão adicionada com sucesso.')
            return redirect('lista_sessoes')
    else:
        form = SessaoForm()
    return render(request, 'sessoes_front/adicionar_sessao.html', {'form': form})


@user_passes_test(eh_admin)
def editar_sessao(request, sessaoid):
    sessao = Sessoes.objects.get(sessaoid=sessaoid)
    if request.method == 'POST':
        form = SessaoForm(request.POST, instance=sessao)
        if form.is_valid():
            # Get the cleaned data
            data = form.cleaned_data

            # Update using raw SQL to handle time -> timestamp conversion
            # Preserve the date part from the existing record
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE sessoes 
                    SET salaid = %s, 
                        filmeid = %s, 
                        inicio = DATE(inicio) + %s::time, 
                        fim = DATE(fim) + %s::time,
                        versao = %s,
                        estadosessao = %s,
                        precosessao = %s
                    WHERE sessaoid = %s
                """, [
                    data['salaid'].salaid if data['salaid'] else None,
                    data['filmeid'].filmeid if data['filmeid'] else None,
                    str(data['inicio']),
                    str(data['fim']),
                    data['versao'],
                    data['estadosessao'],
                    data['precosessao'],
                    sessaoid
                ])

            messages.success(request, f'Sessão #{sessaoid} atualizada com sucesso.')
            return redirect('lista_sessoes')
    else:
        form = SessaoForm(instance=sessao)
    return render(request, 'sessoes_front/editar_sessao.html', {'form': form, 'sessao': sessao})


@user_passes_test(eh_admin)
def remover_sessao(request, sessaoid):
    sessao = Sessoes.objects.get(sessaoid=sessaoid)

    if request.method == 'POST':
        try:
            # Check for related objects before attempting deletion
            bilhetes_count = sessao.bilhetes.count()

            if bilhetes_count > 0:
                error_msg = f"Não é possível remover esta sessão porque possui dados relacionados: {bilhetes_count} bilhete(s)."
                messages.error(request, error_msg)
                return render(request, 'sessoes_front/confirmar_delete_sessao.html', {'sessao': sessao})

            # If no related objects, proceed with deletion
            sessao.delete()

            # Reset the auto-increment sequence for PostgreSQL
            with connection.cursor() as cursor:
                cursor.execute("SELECT setval(pg_get_serial_sequence('sessoes', 'sessaoid'), COALESCE((SELECT MAX(sessaoid) FROM sessoes), 1), false);")

            messages.success(request, f'Sessão #{sessao.sessaoid} foi removida com sucesso.')
            return redirect('lista_sessoes')

        except ProtectedError as e:
            messages.error(request, 'Não é possível remover esta sessão porque possui dados relacionados.')
            return render(request, 'sessoes_front/confirmar_delete_sessao.html', {'sessao': sessao})

    # GET request - show confirmation page with related objects info
    bilhetes_count = sessao.bilhetes.count()

    context = {
        'sessao': sessao,
        'bilhetes_count': bilhetes_count,
        'has_related_objects': bilhetes_count > 0
    }

    return render(request, 'sessoes_front/confirmar_delete_sessao.html', context)

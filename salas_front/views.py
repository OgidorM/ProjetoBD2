from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.db import connection
from bd2ap1.models import Salas
from .forms import SalaForm

def index(request):
    return redirect('listar_salas')

def lista_salas(request):
    salas = Salas.objects.select_related('cinemaid').order_by('salaid')
    return render(request, 'salas_front/lista_salas.html', {'salas': salas})

@login_required
def adicionar_sala(request):
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_salas')
    else:
        form = SalaForm()
    return render(request, 'salas_front/adicionar_sala.html', {'form': form})

@login_required
def editar_sala(request, salaid):
    salas = Salas.objects.get(pk=salaid)
    if request.method == 'POST':
        form = SalaForm(request.POST, instance=salas)
        if form.is_valid():
            form.save()
            return redirect('lista_salas')
    else:
        form = SalaForm(instance=salas)
    return render(request, 'salas_front/editar_sala.html', {'form': form, 'salas': salas})

@login_required
def remover_sala(request, salaid):
    salas = Salas.objects.get(salaid=salaid)

    if request.method == 'POST':
        try:
            # Check for related objects before attempting deletion
            lugares_count = salas.lugares.count()
            sessoes_count = salas.sessoes.count()

            if lugares_count > 0 or sessoes_count > 0:
                error_msg = f"Não é possível remover esta sala porque possui dados relacionados: "
                related_items = []
                if lugares_count > 0:
                    related_items.append(f"{lugares_count} lugar(es)")
                if sessoes_count > 0:
                    related_items.append(f"{sessoes_count} sessão(ões)")
                error_msg += " e ".join(related_items) + "."
                messages.error(request, error_msg)
                return render(request, 'salas_front/confirmar_delete_sala.html', {'salas': salas})

            # If no related objects, proceed with deletion
            salas.delete()

            # Reset the auto-increment sequence for PostgreSQL
            with connection.cursor() as cursor:
                cursor.execute("SELECT setval(pg_get_serial_sequence('salas', 'salaid'), COALESCE((SELECT MAX(salaid) FROM salas), 1), false);")

            messages.success(request, f'Sala "{salas.nomesala}" foi removida com sucesso.')
            return redirect('lista_salas')

        except ProtectedError as e:
            messages.error(request, 'Não é possível remover esta sala porque possui dados relacionados.')
            return render(request, 'salas_front/confirmar_delete_sala.html', {'salas': salas})

    # GET request - show confirmation page with related objects info
    lugares_count = salas.lugares.count()
    sessoes_count = salas.sessoes.count()

    context = {
        'salas': salas,
        'lugares_count': lugares_count,
        'sessoes_count': sessoes_count,
        'has_related_objects': lugares_count > 0 or sessoes_count > 0
    }

    return render(request, 'salas_front/confirmar_delete_sala.html', context)

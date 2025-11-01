from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.db import connection
from bd2ap1.models import Lugares
from .forms import LugarForm

def index(request):
    return redirect('lista_lugares')

def lista_lugares(request):
    lugares = Lugares.objects.select_related('salaid').order_by('lugarid')
    return render(request, 'lugares_front/lista_lugares.html', {'lugares': lugares})

def adicionar_lugar(request):
    if request.method == 'POST':
        form = LugarForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_lugares')
    else:
        form = LugarForm()
    return render(request, 'lugares_front/adicionar_lugar.html', {'form': form})

def editar_lugar(request, lugarid):
    lugar = Lugares.objects.get(lugarid=lugarid)
    if request.method == 'POST':
        form = LugarForm(request.POST, instance=lugar)
        if form.is_valid():
            form.save()
            return redirect('lista_lugares')
    else:
        form = LugarForm(instance=lugar)
    return render(request, 'lugares_front/editar_lugar.html', {'form': form, 'lugar': lugar})

def remover_lugar(request, lugarid):
    lugar = Lugares.objects.get(lugarid=lugarid)

    if request.method == 'POST':
        try:
            # Check for related objects before attempting deletion
            bilhetes_count = lugar.bilhetes.count()

            if bilhetes_count > 0:
                error_msg = f"Não é possível remover este lugar porque possui {bilhetes_count} bilhete(s) relacionado(s)."
                messages.error(request, error_msg)
                return render(request, 'lugares_front/confirmar_delete_lugar.html', {'lugar': lugar})

            # If no related objects, proceed with deletion
            lugar.delete()

            # Reset the auto-increment sequence for PostgreSQL
            with connection.cursor() as cursor:
                cursor.execute("SELECT setval(pg_get_serial_sequence('lugares', 'lugarid'), COALESCE((SELECT MAX(lugarid) FROM lugares), 1), false);")

            messages.success(request, f'Lugar #{lugar.lugarid} (Sala {lugar.salaid}, {lugar.fila}{lugar.numero}) foi removido com sucesso.')
            return redirect('lista_lugares')

        except ProtectedError as e:
            messages.error(request, 'Não é possível remover este lugar porque possui dados relacionados.')
            return render(request, 'lugares_front/confirmar_delete_lugar.html', {'lugar': lugar})

    # GET request - show confirmation page with related objects info
    bilhetes_count = lugar.bilhetes.count()

    context = {
        'lugar': lugar,
        'bilhetes_count': bilhetes_count,
        'has_related_objects': bilhetes_count > 0
    }

    return render(request, 'lugares_front/confirmar_delete_lugar.html', context)

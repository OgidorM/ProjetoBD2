from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models.deletion import ProtectedError

from bd2ap1.models import Lugares
from bd2ap1.mongo_logger import log_action
from .forms import LugarForm


@login_required
def index(request):
    return redirect('lista_lugares')


@login_required
def lista_lugares(request):
    lugares = Lugares.objects.select_related('salaid').order_by('lugarid')
    return render(request, 'lugares_front/lista_lugares.html', {'lugares': lugares})


@login_required
def adicionar_lugar(request):
    if request.method == 'POST':
        form = LugarForm(request.POST)
        if form.is_valid():
            lugar = form.save()

            log_action(
                user=request.user,
                action='CREATE',
                target_model='Lugar',
                target_id=lugar.lugarid,
                details={'fila': lugar.fila, 'numero': lugar.numero, 'sala': str(lugar.salaid)}
            )
            return redirect('lista_lugares')
    else:
        form = LugarForm()
    return render(request, 'lugares_front/adicionar_lugar.html', {'form': form})


@login_required
def editar_lugar(request, lugarid):
    lugar = get_object_or_404(Lugares, lugarid=lugarid)
    if request.method == 'POST':
        form = LugarForm(request.POST, instance=lugar)
        if form.is_valid():
            form.save()

            log_action(
                user=request.user,
                action='UPDATE',
                target_model='Lugar',
                target_id=lugar.lugarid,
                details={'estado': lugar.estadolugar}
            )
            return redirect('lista_lugares')
    else:
        form = LugarForm(instance=lugar)
    return render(request, 'lugares_front/editar_lugares.html', {'form': form, 'lugar': lugar})


@login_required
def remover_lugar(request, lugarid):
    lugar = get_object_or_404(Lugares, lugarid=lugarid)

    bilhetes_count = lugar.bilhetes.count()

    if request.method == 'POST':
        try:
            info_lugar = f"{lugar.fila}{lugar.numero}"
            lugar.delete()

            log_action(
                user=request.user,
                action='DELETE',
                target_model='Lugar',
                target_id=lugarid,
                details={'lugar': info_lugar, 'bilhetes_afetados': bilhetes_count}
            )

            messages.success(request, f'Lugar {info_lugar} removido. Bilhetes associados foram limpos.')
            return redirect('lista_lugares')

        except ProtectedError:
            messages.error(request, 'Não é possível remover este lugar devido a restrições de integridade.')
            return render(request, 'lugares_front/confirmar_delete_lugares.html',
                          {'lugar': lugar, 'has_related_objects': True})

    context = {
        'lugar': lugar,
        'bilhetes_count': bilhetes_count,
        'has_related_objects': bilhetes_count > 0
    }

    return render(request, 'lugares_front/confirmar_delete_lugares.html', context)

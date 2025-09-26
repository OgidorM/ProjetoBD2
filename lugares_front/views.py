from django.shortcuts import render, redirect
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
    return render(request, 'lugares_front/editar_lugar.html', {'form': form, 'lugares': lugar})

def remover_lugar(request, lugarid):
    lugar = Lugares.objects.get(lugarid=lugarid)
    if request.method == 'POST':
        lugar.delete()
        return redirect('lista_lugares')
    return render(request, 'lugares_front/confirmar_delete_lugar.html', {'lugares': lugar})

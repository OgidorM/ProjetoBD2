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

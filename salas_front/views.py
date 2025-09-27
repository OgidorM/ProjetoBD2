from django.shortcuts import render, redirect
from bd2ap1.models import Salas
from .forms import SalaForm

def index(request):
    return redirect('listar_salas')

def lista_salas(request):
    salas = Salas.objects.select_related('cinemaid').order_by('salaid')
    return render(request, 'salas_front/lista_salas.html', {'salas': salas})

def adicionar_sala(request):
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_salas')
    else:
        form = SalaForm()
    return render(request, 'salas_front/adicionar_sala.html', {'form': form})

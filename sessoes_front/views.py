
from django.shortcuts import render, redirect
from bd2ap1.models import Sessoes
from .forms import SessaoForm

def index(request):
    return redirect('lista_sessoes')

def lista_sessoes(request):
    sessoes = Sessoes.objects.select_related('filmeid', 'salaid').order_by('sessaoid')
    return render(request, 'sessoes_front/lista_sessoes.html', {'sessoes': sessoes})

def adicionar_sessao(request):
    if request.method == 'POST':
        form = SessaoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_sessoes')
    else:
        form = SessaoForm()
    return render(request, 'sessoes_front/adicionar_sessao.html', {'form': form})

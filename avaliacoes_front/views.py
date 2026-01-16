from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from bd2ap1.models import Avaliacoes
from .forms import AvaliacaoForm

@login_required
def index(request):
    return redirect('lista_avaliacoes')

@login_required
def lista_avaliacoes(request):
    avaliacoes = Avaliacoes.objects.select_related('venda').order_by('avaliacaoid')
    return render(request, 'avaliacoes_front/lista_avaliacoes.html', {'avaliacoes': avaliacoes})

@login_required
def adicionar_avaliacao(request):
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_avaliacoes')
    else:
        form = AvaliacaoForm()
    return render(request, 'avaliacoes_front/adicionar_avaliacao.html', {'form': form})
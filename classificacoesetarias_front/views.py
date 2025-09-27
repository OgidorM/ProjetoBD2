
from django.shortcuts import render, redirect
from bd2ap1.models import ClassificacoesEtarias
from .forms import ClassificacaoEtariaForm

def index(request):
    return redirect('lista_classificacoesetarias')

def lista_classificacoesetarias(request):
    classificacoes = ClassificacoesEtarias.objects.order_by('classificacaoid')
    return render(request, 'classificacoesetarias_front/lista_classificacoesetarias.html', {'classificacoes': classificacoes})

def adicionar_classificacaoetaria(request):
    if request.method == 'POST':
        form = ClassificacaoEtariaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_classificacoesetarias')
    else:
        form = ClassificacaoEtariaForm()
    return render(request, 'classificacoesetarias_front/adicionar_classificacaoetaria.html', {'form': form})

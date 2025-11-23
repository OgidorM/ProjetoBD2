from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from bd2ap1.models import Vendas
from .forms import VendaForm


@login_required
def index(request):
    return redirect('lista_vendas')

def lista_vendas(request):
    vendas = Vendas.objects.select_related('clienteid', 'funcionarioid').order_by('vendaid')
    return render(request, 'vendas_front/lista_vendas.html', {'vendas': vendas})

def adicionar_venda(request):
    if request.method == 'POST':
        form = VendaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_vendas')
    else:
        form = VendaForm()
    return render(request, 'vendas_front/adicionar_venda.html', {'form': form})
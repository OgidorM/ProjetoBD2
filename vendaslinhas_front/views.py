from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from bd2ap1.models import VendaLinhas
from .forms import VendaLinhaForm

@login_required
def index(request):
    return redirect('lista_vendaslinhas')

def lista_vendaslinhas(request):
    vendaslinhas = VendaLinhas.objects.select_related('vendaid', 'produtoid').order_by('vendalinhaid')
    return render(request, 'vendaslinhas_front/lista_vendaslinhas.html', {'vendaslinhas': vendaslinhas})

def adicionar_vendalinha(request):
    if request.method == 'POST':
        form = VendaLinhaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_vendaslinhas')
    else:
        form = VendaLinhaForm()
    return render(request, 'vendaslinhas_front/adicionar_vendalinha.html', {'form': form})
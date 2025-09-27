from django.shortcuts import render, redirect
from bd2ap1.models import Bilhetes
from .forms import BilheteForm

def index(request):
    return redirect('listar_bilhetes')

def lista_bilhetes(request):
    bilhetes = Bilhetes.objects.select_related('sessaoid','lugarid').order_by('bilheteid')
    return render(request, 'bilhetes_front/lista_bilhetes.html', {'bilhetes': bilhetes})

def adicionar_bilhete(request):
    if request.method == 'POST':
        form = BilheteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_bilhetes')
    else:
        form = BilheteForm()
    return render(request, 'bilhetes_front/adicionar_bilhete.html', {'form': form})

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

def editar_bilhete(request, bilheteid):
    bilhete = Bilhetes.objects.get(bilheteid=bilheteid)
    if request.method == 'POST':
        form = BilheteForm(request.POST, instance=bilhete)
        if form.is_valid():
            form.save()
            return redirect('lista_bilhetes')
    else:
        form = BilheteForm(instance=bilhete)
    return render(request, 'bilhetes_front/editar_bilhete.html', {'form': form, 'bilhete': bilhete})

def remover_bilhete(request, bilheteid):
    bilhete = Bilhetes.objects.get(bilheteid=bilheteid)
    if request.method == 'POST':
        bilhete.delete()
        return redirect('lista_bilhetes')
    return render(request, 'bilhetes_front/confirmar_delete_bilhete.html', {'bilhete': bilhete})


from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.db import connection
from bd2ap1.models import Bilhetes
from .forms import BilheteForm

def index(request):
    return redirect('listar_bilhetes')

def lista_bilhetes(request):
    bilhetes = Bilhetes.objects.select_related(
        'lugarid__sessaoid',  
        'lugarid__lugarid'    
    ).order_by('bilheteid')
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
        try:
            # Check for related objects before attempting deletion
            vendalinhas_count = bilhete.linhas_venda.count()

            if vendalinhas_count > 0:
                error_msg = f"Não é possível remover este bilhete porque possui dados relacionados: {vendalinhas_count} venda linha(s)."
                messages.error(request, error_msg)
                return render(request, 'bilhetes_front/confirmar_delete_bilhete.html', {'bilhete': bilhete})

            # If no related objects, proceed with deletion
            bilhete.delete()

            # Reset the auto-increment sequence for PostgreSQL
            with connection.cursor() as cursor:
                cursor.execute("SELECT setval(pg_get_serial_sequence('bilhetes', 'bilheteid'), COALESCE((SELECT MAX(bilheteid) FROM bilhetes), 1), false);")

            messages.success(request, f'Bilhete #{bilhete.bilheteid} foi removido com sucesso.')
            return redirect('lista_bilhetes')

        except ProtectedError as e:
            messages.error(request, 'Não é possível remover este bilhete porque possui dados relacionados.')
            return render(request, 'bilhetes_front/confirmar_delete_bilhete.html', {'bilhete': bilhete})

    # GET request - show confirmation page with related objects info
    vendalinhas_count = bilhete.linhas_venda.count()

    context = {
        'bilhete': bilhete,
        'vendalinhas_count': vendalinhas_count,
        'has_related_objects': vendalinhas_count > 0
    }

    return render(request, 'bilhetes_front/confirmar_delete_bilhete.html', context)

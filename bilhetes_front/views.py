from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.db import connection

from bd2ap1.models import Bilhetes
from bd2ap1.mongo_logger import log_action
from .forms import BilheteForm


def eh_admin(user):
    return user.is_staff or user.is_superuser


@user_passes_test(eh_admin)
def index(request):
    return redirect('lista_bilhetes')


def lista_bilhetes(request):
    bilhetes = Bilhetes.objects.select_related('sessaoid', 'lugarid').order_by('bilheteid')
    return render(request, 'bilhetes_front/lista_bilhetes.html', {'bilhetes': bilhetes})


@user_passes_test(eh_admin)
def adicionar_bilhete(request):
    if request.method == 'POST':
        form = BilheteForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            lugar_sessao = data['lugarid'] # This is a LugaresSessao object from the form queryset
            
            with connection.cursor() as cursor:
                cursor.execute("CALL inserir_bilhete(%s, %s, %s)", [
                    lugar_sessao.lugarsessaoid,
                    lugar_sessao.sessaoid.sessaoid,
                    data['precobilhete']
                ])

            return redirect('lista_bilhetes')
    else:
        form = BilheteForm()
    return render(request, 'bilhetes_front/adicionar_bilhete.html', {'form': form})


@user_passes_test(eh_admin)
def editar_bilhete(request, bilheteid):
    bilhete = get_object_or_404(Bilhetes, bilheteid=bilheteid)
    if request.method == 'POST':
        form = BilheteForm(request.POST, instance=bilhete)
        if form.is_valid():
            form.save()

            log_action(
                user=request.user,
                action='UPDATE',
                target_model='Bilhete',
                target_id=bilhete.bilheteid,
                details={'novo_preco': float(bilhete.precobilhete)}
            )

            return redirect('lista_bilhetes')
    else:
        form = BilheteForm(instance=bilhete)
    return render(request, 'bilhetes_front/editar_bilhete.html', {'form': form, 'bilhete': bilhete})


@user_passes_test(eh_admin)
def remover_bilhete(request, bilheteid):
    bilhete = get_object_or_404(Bilhetes, bilheteid=bilheteid)

    vendalinhas_count = bilhete.linhas_venda.count()
    bilhete_preco = float(bilhete.precobilhete)

    if request.method == 'POST':
        try:
            bilhete.delete()

            log_action(
                user=request.user,
                action='DELETE',
                target_model='Bilhete',
                target_id=bilheteid,
                details={'preco': bilhete_preco, 'tipo': 'SET_NULL_VENDAS'}
            )

            messages.success(request, f'Bilhete #{bilheteid} removido. O registo financeiro da venda foi mantido.')
            return redirect('lista_bilhetes')

        except ProtectedError:
            messages.error(request, 'Erro de integridade ao tentar remover o bilhete.')
            return render(request, 'bilhetes_front/confirmar_delete_bilhete.html',
                          {'bilhete': bilhete, 'has_related_objects': True})

    # GET request
    context = {
        'bilhete': bilhete,
        'vendalinhas_count': vendalinhas_count,
        'has_related_objects': vendalinhas_count > 0
    }

    return render(request, 'bilhetes_front/confirmar_delete_bilhete.html', context)

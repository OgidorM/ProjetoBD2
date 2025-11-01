
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.db import connection
from bd2ap1.models import Categorias
from .forms import CategoriaForm

def index(request):
    return redirect('lista_categorias')

def lista_categorias(request):
    categorias = Categorias.objects.order_by('categoriaid')
    return render(request, 'categorias_front/lista_categorias.html', {'categorias': categorias})

def adicionar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'categorias_front/adicionar_categoria.html', {'form': form})

def editar_categoria(request, categoriaid):
    categoria = Categorias.objects.get(categoriaid=categoriaid)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'categorias_front/editar_categoria.html', {'form': form, 'categoria': categoria})

def remover_categoria(request, categoriaid):
    categoria = Categorias.objects.get(categoriaid=categoriaid)

    if request.method == 'POST':
        try:
            # Check for related objects before attempting deletion
            filmes_count = categoria.filmes.count()

            if filmes_count > 0:
                error_msg = f"Não é possível remover esta categoria porque possui {filmes_count} filme(s) relacionado(s)."
                messages.error(request, error_msg)
                return render(request, 'categorias_front/confirmar_delete_categoria.html', {'categoria': categoria})

            # If no related objects, proceed with deletion
            categoria.delete()

            # Reset the auto-increment sequence for PostgreSQL
            with connection.cursor() as cursor:
                cursor.execute("SELECT setval(pg_get_serial_sequence('categorias', 'categoriaid'), COALESCE((SELECT MAX(categoriaid) FROM categorias), 1), false);")

            messages.success(request, f'Categoria "{categoria.nomecategoria}" foi removida com sucesso.')
            return redirect('lista_categorias')

        except ProtectedError as e:
            messages.error(request, 'Não é possível remover esta categoria porque possui dados relacionados.')
            return render(request, 'categorias_front/confirmar_delete_categoria.html', {'categoria': categoria})

    # GET request - show confirmation page with related objects info
    filmes_count = categoria.filmes.count()

    context = {
        'categoria': categoria,
        'filmes_count': filmes_count,
        'has_related_objects': filmes_count > 0
    }

    return render(request, 'categorias_front/confirmar_delete_categoria.html', context)


from django.shortcuts import render, redirect
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

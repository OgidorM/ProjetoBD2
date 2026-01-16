from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from bd2ap1.models import Produtos
from .forms import ProdutoForm

@login_required
def index(request):
    return redirect('lista_produtos')

@login_required
def lista_produtos(request):
    produtos = Produtos.objects.all().order_by('produtoid')
    return render(request, 'produtos_front/lista_produtos.html', {'produtos': produtos})

@login_required
def adicionar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_produtos')
    else:
        form = ProdutoForm()
    return render(request, 'produtos_front/adicionar_produto.html', {'form': form})
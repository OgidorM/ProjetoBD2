from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from bd2ap1.models import Produtos
from .forms import ProdutoForm

def eh_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(eh_admin)
def index(request):
    return redirect('lista_produtos')


def lista_produtos(request):
    produtos = Produtos.objects.all().order_by('produtoid')
    return render(request, 'produtos_front/lista_produtos.html', {'produtos': produtos})

@user_passes_test(eh_admin)
def adicionar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_produtos')
    else:
        form = ProdutoForm()
    return render(request, 'produtos_front/adicionar_produto.html', {'form': form})
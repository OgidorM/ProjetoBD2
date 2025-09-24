from django.shortcuts import render
from bd2ap1.models import Filmes
from .forms import FilmeForm

def index(request):
    return render(request, 'filmes_front/index.html')

def lista_filmes(request):
    filmes = Filmes.objects.all()
    return render(request, 'filmes_front/lista_filmes.html', {'filmes': filmes})

def adicionar_filme(request):
    if request.method == 'POST':
        form = FilmeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_filmes')
    else:
        form = FilmeForm()
    return render(request, 'filmes_front/adicionar_filme.html', {'form': form})
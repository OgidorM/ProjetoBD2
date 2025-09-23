from django.shortcuts import render

def index(request):
    return render(request, 'filmes_front/index.html')

def lista_filmes(request):
    # dados estáticos de exemplo
    filmes = [
        {'titulo': 'Matrix', 'categoria': 'Ficção Científica', 'duracao': 136},
        {'titulo': 'Titanic', 'categoria': 'Romance', 'duracao': 195},
        {'titulo': 'O Poderoso Chefão', 'categoria': 'Crime', 'duracao': 175},
    ]
    return render(request, 'filmes_front/lista_filmes.html', {'filmes': filmes})

def adicionar_filme(request):
    return render(request, 'filmes_front/adicionar_filme.html')
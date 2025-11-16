from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Filmes
from .serializers import FilmesSerializer

def index(request):
    return render(request, 'core/index.html')

def home(request):
    return render(request, 'core/index.html')


@api_view(['GET'])
def filmes_api(request):
    """
    API endpoint to get all movies in JSON format
    """
    filmes = Filmes.objects.select_related('categoriaid', 'classificacaoetaria', 'cinemaid').all()
    serializer = FilmesSerializer(filmes, many=True)
    return Response(serializer.data)


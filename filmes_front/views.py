from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

from bd2ap1.models import Filmes
from .forms import FilmeForm
from .services import FilmeImportService



def index(request):
    return redirect('lista_filmes')



def lista_filmes(request):
    filmes = Filmes.objects.all()
    return render(request, 'filmes_front/lista_filmes.html', {'filmes': filmes})


@login_required
def adicionar_filme(request):
    if request.method == 'POST':
        form = FilmeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_filmes')
    else:
        form = FilmeForm()
    return render(request, 'filmes_front/adicionar_filme.html', {'form': form})


@login_required
def importar_sinopses(request):
    is_json = 'application/json' in request.headers.get('Accept', '')
    
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        overwrite = bool(request.POST.get('overwrite'))
        encoding = 'utf-8'

        if not csv_file:
            msg = 'Selecione um ficheiro CSV para importar.'
            if is_json:
                return JsonResponse({'error': msg}, status=400)
            messages.error(request, msg)
            return redirect('importar_sinopses')

        import tempfile

        try:
            with tempfile.NamedTemporaryFile(delete=True, suffix='.csv') as tmp:
                for chunk in csv_file.chunks():
                    tmp.write(chunk)
                tmp.flush()

                service = FilmeImportService()
                result = service.import_sinopses_from_csv(tmp.name, overwrite=overwrite, encoding=encoding)

            msg_success = (
                f"Import concluído. Processadas={result.processed}, Atualizadas={result.updated}, "
                f"Ignoradas(existentes)={result.skipped_existing}, Falhas={result.not_found}."
            )
            
            warnings = []
            if result.missing_required:
                warnings.append('Linhas inválidas (faltou título ou sinopse): ' + ', '.join(result.missing_required))
            if result.ambiguous_titles:
                warnings.append('Títulos duplicados (ambíguos): ' + ', '.join(result.ambiguous_titles))
            if result.titles_not_found:
                warnings.append('Títulos não encontrados na BD: ' + ', '.join(result.titles_not_found))

            if is_json:
                return JsonResponse({
                    'message': msg_success,
                    'warnings': warnings,
                    'stats': {
                        'processed': result.processed,
                        'updated': result.updated,
                        'skipped': result.skipped_existing,
                        'not_found': result.not_found
                    }
                })

            messages.success(request, msg_success)
            for w in warnings:
                messages.warning(request, w)

            return redirect('lista_filmes')
        except ValueError as e:
            if is_json:
                return JsonResponse({'error': str(e)}, status=400)
            messages.error(request, str(e))
        except UnicodeDecodeError:
            msg = 'Erro ao ler o CSV (UTF-8). Confirme o encoding do ficheiro.'
            if is_json:
                return JsonResponse({'error': msg}, status=400)
            messages.error(request, msg)
        except Exception as e:
            msg = f'Erro ao importar: {e}'
            if is_json:
                return JsonResponse({'error': msg}, status=500)
            messages.error(request, msg)

    return render(request, 'filmes_front/importar_sinopses.html')


def filme_detalhe_api(request, filme_id: int):
    filme = Filmes.objects.select_related('categoriaid', 'cinemaid', 'classificacaoetaria').filter(pk=filme_id).first()
    if not filme:
        return JsonResponse({'error': 'Filme não encontrado'}, status=404)

    return JsonResponse({
        'filmeid': filme.filmeid,
        'titulo': filme.titulo,
        'sinopse': filme.sinopse or '',
        'duracao': filme.duracao,
        'categoria': getattr(filme.categoriaid, 'nomecategoria', None),
        'cinema': getattr(filme.cinemaid, 'nomecinema', None),
        'classificacao': getattr(filme.classificacaoetaria, 'nomeclassificacao', None),
    })

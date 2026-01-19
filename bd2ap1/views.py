from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework import status

# Imports dos Models
from .models import (
    Filmes, Sessoes, LugaresSessao, Vendas, VendaLinhas,
    Bilhetes, Clientes, Funcionarios, Lugares, Salas,
    Cinemas, Produtos, Avaliacoes, Categorias, ClassificacoesEtarias
)
from .serializers import (
    FilmesSerializer, SessoesSerializer, LugaresSessaoSerializer,
    SessaoCreateSerializer, SalasSerializer, CinemasSerializer, ProdutosSerializer
)
from .mongo_logger import log_action
from .omdb_service import fetch_movie_data

# --- ARQUITETURA NOVA (Imports) ---
from clientes.models import ClienteProfile
from clientes.core.services import ClienteService
from clientes.core.dtos import NovoClienteDTO
from clientes.core.exceptions import ClienteServiceException


# ==============================================================================
#  ÁREA 1: FRONTEND LEGADO (DJANGO TEMPLATES / HTML)
# ==============================================================================

def index(request):
    return render(request, 'core/index.html')


def home(request):
    return render(request, 'core/index.html')


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        # 1. O Django cria o User padrão
        response = super().form_valid(form)
        user = self.object

        # 2. Sincronização: Criar o vínculo para o sistema novo funcionar
        try:
            if not ClienteProfile.objects.filter(user=user).exists():
                email = form.cleaned_data.get('email', '')
                # Cria na tabela legada
                cliente = Clientes.objects.create(
                    nomecliente=user.username,
                    emailcliente=email
                )
                # Cria o vínculo
                ClienteProfile.objects.create(user=user, cliente_dados=cliente)

                log_action(user, 'signup_legacy', 'User', user.id, {"email": email})
        except Exception:
            # Se falhar a sincronia, não impedimos o cadastro básico
            pass

        return response


# ==============================================================================
#  ÁREA 2: API PARA O REACT (AUTH & PERFIL) - AGORA COMPLETA
# ==============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    """ Endpoint para Login via React (Retorna JSON + Cookie de Sessão) """
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)  # Cria o cookie sessionid
        log_action(user, 'login_api', 'User', user.id, {"status": "success"})

        # Verifica se é staff para o frontend saber se mostra o painel admin
        return Response({
            "message": "Login successful",
            "username": user.username,
            "id": user.id,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser
        })
    else:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_api(request):
    """
    Endpoint para Registo via React (USA A ARQUITETURA LIMPA)
    """
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')

    dto = NovoClienteDTO(
        username=username,
        password=password,
        email=email,
        nome_completo=username  # Usa username como nome inicial
    )

    service = ClienteService()
    try:
        # Service cria User + Cliente + Profile numa transação segura
        profile = service.registrar_novo_cliente(dto)

        log_action(profile.user, 'signup_api', 'User', profile.user.id, {"email": email})

        # Auto-login após registo
        login(request, profile.user)

        return Response({
            "message": "User created successfully",
            "username": profile.user.username,
            "id": profile.user.id,
            "is_staff": False
        }, status=status.HTTP_201_CREATED)

    except ClienteServiceException as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_api(request):
    logout(request)
    return Response({"message": "Logout successful"})


@api_view(['GET'])
@permission_classes([AllowAny])
def whoami_api(request):
    """ Endpoint para o React validar a sessão atual """
    if not request.user.is_authenticated:
        return Response({"is_authenticated": False})

    service = ClienteService()
    profile = service.get_cliente_por_user(request.user)

    return Response({
        "is_authenticated": True,
        "username": request.user.username,
        "is_staff": request.user.is_staff,
        "cliente_id": profile.cliente_dados.clienteid if profile else None,
        "session_key": request.session.session_key
    })


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def update_profile_api(request):
    """ API to update user profile data """
    try:
        user = request.user
        username = request.data.get('username')
        email = request.data.get('email')

        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if username is already taken by another user
        if User.objects.filter(username=username).exclude(pk=user.id).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            old_username = user.username

            # Update User model
            user.username = username
            user.email = email
            user.save()

            # Update corresponding Cliente record
            try:
                # Tenta via arquitetura nova
                profile = ClienteProfile.objects.get(user=user)
                cliente = profile.cliente_dados
                cliente.nomecliente = username
                cliente.emailcliente = email
                cliente.save()
            except ClienteProfile.DoesNotExist:
                # Fallback antigo
                cliente = Clientes.objects.filter(nomecliente=old_username).first()
                if cliente:
                    cliente.nomecliente = username
                    cliente.emailcliente = email
                    cliente.save()

            log_action(user, 'update_profile', 'User', user.id,
                       {"old_username": old_username, "new_username": username})

            return Response({
                "message": "Profile updated successfully",
                "username": user.username,
                "email": user.email
            })

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
#  ÁREA 3: API ENDPOINTS DE NEGÓCIO (VENDAS, FILMES, ETC)
# ==============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def produtos_api(request):
    """API endpoint to get all active products"""
    produtos = Produtos.objects.filter(ativo=True, stock__gt=0)
    serializer = ProdutosSerializer(produtos, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def comprar_produtos_api(request):
    """
    API to process a purchase of concession items
    """
    try:
        user = request.user
        items = request.data.get('items', [])  # List of {produtoid, quantidade}

        if not items:
            return Response({"error": "No items provided"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # --- CORREÇÃO DE ARQUITETURA ---
            try:
                profile = ClienteProfile.objects.select_related('cliente_dados').get(user=user)
                cliente = profile.cliente_dados
            except ClienteProfile.DoesNotExist:
                # Fallback para admin ou users antigos
                cliente = Clientes.objects.filter(nomecliente=user.username).first()
                if not cliente:
                    cliente = Clientes.objects.create(nomecliente=user.username, emailcliente=user.email)
            # -------------------------------

            venda = Vendas.objects.create(
                clienteid=cliente,
                data=timezone.now().date(),
                estadovenda='Concluída',
                totalvenda=0
            )

            total = 0
            for item in items:
                produto = Produtos.objects.select_for_update().get(pk=item['produtoid'])
                qty = int(item['quantidade'])

                if produto.stock < qty:
                    raise Exception(f"Insufficient stock for {produto.nomeproduto}")

                produto.stock -= qty
                produto.save()

                line_total = produto.precoproduto * qty
                VendaLinhas.objects.create(
                    vendaid=venda,
                    produtoid=produto,
                    quantidade=qty,
                    precolinha=produto.precoproduto,
                    total_linha=line_total
                )
                total += line_total

            venda.totalvenda = total
            venda.save()

            log_action(user, 'buy_concessions', 'Vendas', venda.vendaid, {"total": float(total)})

            return Response({"message": "Purchase successful", "venda_id": venda.vendaid},
                            status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def filmes_api(request):
    cinema_id = request.query_params.get('cinema')
    
    # If admin/staff, return all movies. Otherwise, only movies with future sessions.
    if request.user.is_staff:
        queryset = Filmes.objects.select_related('categoriaid', 'classificacaoetaria', 'cinemaid')
    else:
        now = timezone.now()
        queryset = Filmes.objects.filter(sessoes__inicio__gte=now).select_related('categoriaid', 'classificacaoetaria', 'cinemaid').distinct()

    if cinema_id:
        queryset = queryset.filter(cinemaid=cinema_id)

    filmes = queryset.all()
    serializer = FilmesSerializer(filmes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def cinemas_api(request):
    cinemas = Cinemas.objects.all()
    serializer = CinemasSerializer(cinemas, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def salas_api(request):
    salas = Salas.objects.all()
    serializer = SalasSerializer(salas, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def sessoes_por_filme_api(request, filmeid):
    try:
        now = timezone.now()
        sessoes = Sessoes.objects.filter(filmeid=filmeid, inicio__gte=now).select_related('salaid__cinemaid').order_by(
            'inicio')
        serializer = SessoesSerializer(sessoes, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def lista_sessoes_api(request):
    now = timezone.now()
    sessoes = Sessoes.objects.filter(inicio__gte=now).select_related('filmeid', 'salaid').order_by('inicio')
    serializer = SessoesSerializer(sessoes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def lugares_sessao_api(request, sessaoid):
    try:
        with transaction.atomic():
            sessao = Sessoes.objects.select_for_update().get(pk=sessaoid)
            lugares_ocupados = LugaresSessao.objects.filter(sessaoid=sessaoid)

            if not lugares_ocupados.exists():
                sala = sessao.salaid
                if sala:
                    lugares = Lugares.objects.filter(salaid=sala)
                    lugares_sessao_novos = [
                        LugaresSessao(lugarid=lugar, sessaoid=sessao, estado='Livre') for lugar in lugares
                    ]
                    LugaresSessao.objects.bulk_create(lugares_sessao_novos)
                    lugares_ocupados = LugaresSessao.objects.filter(sessaoid=sessaoid)

        serializer = LugaresSessaoSerializer(lugares_ocupados.select_related('lugarid'), many=True)
        return Response(serializer.data)
    except Sessoes.DoesNotExist:
        return Response({"error": "Sessão not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def criar_venda_api(request):
    """
    API to process a unified purchase (tickets and/or concessions)
    """
    try:
        user = request.user
        data = request.data
        sessaoid = data.get('sessaoid')
        lugares_ids = data.get('lugares_ids', [])
        products = data.get('products', [])

        if not lugares_ids and not products:
            return Response({"error": "Empty cart"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # --- CORREÇÃO DE ARQUITETURA ---
            try:
                profile = ClienteProfile.objects.select_related('cliente_dados').get(user=user)
                cliente = profile.cliente_dados
            except ClienteProfile.DoesNotExist:
                # Fallback para admin ou users antigos
                cliente = Clientes.objects.filter(nomecliente=user.username).first()
                if not cliente:
                    cliente = Clientes.objects.create(nomecliente=user.username, emailcliente=user.email)
            # -------------------------------

            venda = Vendas.objects.create(
                clienteid=cliente,
                data=timezone.now().date(),
                estadovenda='Concluída',
                totalvenda=0
            )

            total = 0

            # 3. Process Tickets
            if sessaoid and lugares_ids:
                sessao = Sessoes.objects.get(pk=sessaoid)
                price = sessao.precosessao or 10.00

                for ls_id in lugares_ids:
                    # Lock row
                    ls = LugaresSessao.objects.select_for_update().get(pk=ls_id)
                    if ls.estado != 'Livre':
                        lugar_info = f"{ls.lugarid.fila}{ls.lugarid.numero}" if ls.lugarid else "Unknown"
                        raise Exception(f"Lugar {lugar_info} is no longer available")

                    ls.estado = 'Ocupado'
                    ls.save()

                    bilhete = Bilhetes.objects.create(
                        lugarid=ls.lugarid, sessaoid=sessao,
                        precobilhete=price, emissao=timezone.now()
                    )

                    VendaLinhas.objects.create(
                        vendaid=venda, bilheteid=bilhete, quantidade=1,
                        precolinha=price, total_linha=price
                    )
                    total += price

            # 4. Process Concessions
            for item in products:
                produto = Produtos.objects.select_for_update().get(pk=item['produtoid'])
                qty = int(item['quantidade'])

                if produto.stock < qty:
                    raise Exception(f"Insufficient stock for {produto.nomeproduto}")

                produto.stock -= qty
                produto.save()

                line_total = produto.precoproduto * qty
                VendaLinhas.objects.create(
                    vendaid=venda, produtoid=produto, quantidade=qty,
                    precolinha=produto.precoproduto, total_linha=line_total
                )
                total += line_total

            venda.totalvenda = total
            venda.save()

            log_action(user, 'unified_purchase', 'Vendas', venda.vendaid, {"total": float(total)})

            return Response({"message": "Purchase successful", "venda_id": venda.vendaid},
                            status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def minhas_vendas_api(request):
    try:
        # --- CORREÇÃO DE ARQUITETURA ---
        try:
            profile = ClienteProfile.objects.select_related('cliente_dados').get(user=request.user)
            cliente = profile.cliente_dados
        except ClienteProfile.DoesNotExist:
            return Response([])
        # -------------------------------

        vendas = Vendas.objects.filter(clienteid=cliente).order_by('-data', '-vendaid')

        data = []
        for v in vendas:
            linhas = v.linhas.all().select_related('bilheteid__sessaoid__filmeid', 'bilheteid__lugarid', 'produtoid')
            items = []
            for l in linhas:
                if l.bilheteid:
                    items.append({
                        "id": l.bilheteid.bilheteid,
                        "tipo": "ticket",
                        "filme": l.bilheteid.sessaoid.filmeid.titulo,
                        "sala": l.bilheteid.sessaoid.salaid.nomesala if l.bilheteid.sessaoid.salaid else "Sala N/A",
                        "data": l.bilheteid.sessaoid.inicio.isoformat() if l.bilheteid.sessaoid.inicio else None,
                        "lugar": f"{l.bilheteid.lugarid.fila}{l.bilheteid.lugarid.numero}",
                        "preco": l.precolinha
                    })
                elif l.produtoid:
                    items.append({
                        "tipo": "produto",
                        "nome": l.produtoid.nomeproduto,
                        "quantidade": l.quantidade,
                        "preco": l.precolinha
                    })

            calc_total = v.totalvenda or sum(l.precolinha for l in v.linhas.all())

            data.append({
                "id": v.vendaid,
                "data": v.data,
                "total": calc_total,
                "items": items,
                "rated": hasattr(v, 'avaliacao')
            })

        return Response(data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def criar_avaliacao_api(request):
    """
    API to create a review for a purchase
    """
    try:
        user = request.user
        venda_id = request.data.get('venda_id')
        titulo = request.data.get('titulo', 'Avaliação de Compra')
        nota_cinema = request.data.get('nota_cinema')
        nota_filme = request.data.get('nota_filme')
        nota_funcionario = request.data.get('nota_funcionario')
        comentario = request.data.get('comentario', '')

        venda = Vendas.objects.get(pk=venda_id)

        # Verify ownership
        if venda.clienteid.nomecliente != user.username:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        # Check if already rated
        if hasattr(venda, 'avaliacao'):
            return Response({"error": "Sale already rated"}, status=status.HTTP_400_BAD_REQUEST)

        avaliacao = Avaliacoes.objects.create(
            venda=venda,
            tituloavaliacao=titulo,
            avaliacaocinema=nota_cinema,
            avaliacaofilme=nota_filme,
            avaliacaofuncionario=nota_funcionario,
            comentario=comentario
        )

        log_action(user, 'create_review', 'Avaliacoes', avaliacao.avaliacaoid, {"venda_id": venda_id})

        return Response({"message": "Review submitted successfully"}, status=status.HTTP_201_CREATED)

    except Vendas.DoesNotExist:
        return Response({"error": "Sale not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
#  ÁREA 4: ADMIN API (STAFF ONLY)
# ==============================================================================

@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_avaliacoes_api(request):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    avaliacoes = Avaliacoes.objects.all().select_related('venda__clienteid').order_by('-avaliacaoid')
    data = []
    for a in avaliacoes:
        data.append({
            "id": a.avaliacaoid,
            "venda_id": a.venda.vendaid,
            "cliente": a.venda.clienteid.nomecliente if a.venda.clienteid else "Unknown",
            "titulo": a.tituloavaliacao,
            "nota_cinema": a.avaliacaocinema,
            "nota_filme": a.avaliacaofilme,
            "nota_funcionario": a.avaliacaofuncionario,
            "comentario": a.comentario
        })
    return Response(data)


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_funcionarios_api(request):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        funcionarios = Funcionarios.objects.all().select_related('cinemaid')
        data = [{
            "id": f.funcionarioid,
            "nome": f.nomefuncionario,
            "email": f.emailfuncionario,
            "cargo": f.cargo,
            "salario": f.salario,
            "cinema": f.cinemaid.nomecinema if f.cinemaid else 'N/A',
            "cinema_id": f.cinemaid_id
        } for f in funcionarios]
        return Response(data)

    if request.method == 'POST':
        try:
            cinema = Cinemas.objects.get(pk=request.data.get('cinemaid')) if request.data.get('cinemaid') else None
            f = Funcionarios.objects.create(
                nomefuncionario=request.data.get('nome'),
                emailfuncionario=request.data.get('email'),
                telefonefuncionario=request.data.get('telefone', ''),
                cargo=request.data.get('cargo'),
                admissao=timezone.now().date(),
                salario=request.data.get('salario', 0),
                cinemaid=cinema
            )
            return Response({"message": "Funcionário criado", "id": f.funcionarioid}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_create_produto_api(request):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    try:
        p = Produtos.objects.create(
            nomeproduto=request.data.get('nome'),
            precoproduto=request.data.get('preco'),
            stock=request.data.get('stock', 0),
            ativo=True
        )
        return Response({"id": p.produtoid}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_funcionario_detail_api(request, pk):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    try:
        funcionario = Funcionarios.objects.get(pk=pk)
        if request.method == 'DELETE':
            funcionario.delete()
            return Response({"message": "Eliminado"})

        # Update
        funcionario.nomefuncionario = request.data.get('nome', funcionario.nomefuncionario)
        funcionario.cargo = request.data.get('cargo', funcionario.cargo)
        funcionario.salario = request.data.get('salario', funcionario.salario)
        funcionario.save()
        return Response({"message": "Atualizado"})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_clientes_api(request):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        clientes = Clientes.objects.all()
        data = [{
            "id": c.clienteid,
            "nome": c.nomecliente,
            "email": c.emailcliente,
            "telefone": c.telefonecliente,
            "nif": c.nif
        } for c in clientes]
        return Response(data)

    if request.method == 'POST':
        c = Clientes.objects.create(
            nomecliente=request.data.get('nome'),
            emailcliente=request.data.get('email'),
            nif=request.data.get('nif', '')
        )
        return Response({"id": c.clienteid})


@api_view(['POST', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_cliente_detail_api(request, pk):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    try:
        cliente = Clientes.objects.get(pk=pk)
        if request.method == 'DELETE':
            cliente.delete()
            return Response({"message": "Eliminado"})
        cliente.nomecliente = request.data.get('nome', cliente.nomecliente)
        cliente.emailcliente = request.data.get('email', cliente.emailcliente)
        cliente.save()
        return Response({"message": "Atualizado"})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_produto_detail_api(request, pk):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    try:
        produto = Produtos.objects.get(pk=pk)
        if request.method == 'DELETE':
            produto.ativo = False  # Soft delete
            produto.save()
            return Response({"message": "Desativado"})

        # New: support relative stock update if 'stock_change' is provided
        stock_change = request.data.get('stock_change')
        if stock_change is not None:
            new_stock = produto.stock + int(stock_change)
            if new_stock < 0:
                return Response({"error": "Stock cannot be negative"}, status=status.HTTP_400_BAD_REQUEST)
            produto.stock = new_stock
        else:
            # Traditional full update
            produto.nomeproduto = request.data.get('nome', produto.nomeproduto)
            produto.precoproduto = request.data.get('preco', produto.precoproduto)
            produto.stock = request.data.get('stock', produto.stock)

        produto.save()
        return Response({"message": "Atualizado", "new_stock": produto.stock})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_create_movie_api(request):
    """
    API to create a new movie (Admin only)
    """
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    try:
        # Get category and classification
        categoria = Categorias.objects.get(pk=request.data.get('categoriaid'))
        classificacao = ClassificacoesEtarias.objects.get(pk=request.data.get('classificacaoid', 1))

        # Optional Cinema
        cinema_id = request.data.get('cinemaid')
        cinema = Cinemas.objects.get(pk=cinema_id) if cinema_id else None

        movie = Filmes.objects.create(
            titulo=request.data.get('titulo'),
            categoriaid=categoria,
            cinemaid=cinema,
            datalancamento=request.data.get('datalancamento'),
            duracao=request.data.get('duracao'),
            produtora=request.data.get('produtora'),
            idioma=request.data.get('idioma', 'PT'),
            sinopse=request.data.get('sinopse', ''),
            cartaz_url=request.data.get('cartaz_url'),
            classificacaoetaria=classificacao,
            ranking=request.data.get('ranking', 0.0)
        )

        log_action(request.user, 'create_movie', 'Filmes', movie.filmeid, {"titulo": movie.titulo})

        return Response({"message": "Movie created successfully", "id": movie.filmeid}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_vendas_api(request):
    """
    API to list every sale in the system (Admin only)
    """
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    try:
        vendas = Vendas.objects.all().select_related('clienteid').order_by('-data', '-vendaid')
        data = []
        for v in vendas:
            # Reusing the same detailed logic from minhas_vendas but for all sales
            linhas = v.linhas.all().select_related('bilheteid__sessaoid__filmeid', 'bilheteid__sessaoid__salaid',
                                                   'bilheteid__lugarid', 'produtoid')
            items = []
            for l in linhas:
                if l.bilheteid:
                    items.append({
                        "tipo": "ticket",
                        "filme": l.bilheteid.sessaoid.filmeid.titulo,
                        "sala": l.bilheteid.sessaoid.salaid.nomesala,
                        "data": l.bilheteid.sessaoid.inicio,
                        "lugar": f"{l.bilheteid.lugarid.fila}{l.bilheteid.lugarid.numero}",
                        "quantidade": l.quantidade,
                        "preco": l.precolinha
                    })
                elif l.produtoid:
                    items.append({
                        "tipo": "produto",
                        "nome": l.produtoid.nomeproduto,
                        "quantidade": l.quantidade,
                        "preco": l.precolinha
                    })

            # Calculate total from lines if totalvenda is 0 or None
            calc_total = v.totalvenda
            if not calc_total or calc_total == 0:
                calc_total = sum(l.precolinha for l in v.linhas.all())

            data.append({
                "id": v.vendaid,
                "cliente": v.clienteid.nomecliente if v.clienteid else "Unknown",
                "data": v.data,
                "total": calc_total,
                "items": items
            })

        return Response(data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_create_cinema_api(request):
    """
    API to create a new cinema (Admin only)
    """
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    try:
        cinema = Cinemas.objects.create(
            nomecinema=request.data.get('nome'),
            localidadecinema=request.data.get('localidade'),
            emailcinema=request.data.get('email', ''),
            telefonecinema=request.data.get('telefone', ''),
            moradacinema=request.data.get('morada', ''),
            codigopostalcinema=request.data.get('codigo_postal', ''),
            ranking=0.0
        )
        log_action(request.user, 'create_cinema', 'Cinemas', cinema.cinemaid, {"nome": cinema.nomecinema})
        return Response({"message": "Cinema created successfully", "id": cinema.cinemaid},
                        status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_create_room_api(request, cinema_id):
    """
    API to add a room to a cinema (Admin only)
    """
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    try:
        cinema = Cinemas.objects.get(pk=cinema_id)
        room = Salas.objects.create(
            cinemaid=cinema,
            nomesala=request.data.get('nome'),
            capacidade=request.data.get('capacidade', 0),
            filas=request.data.get('filas', 0),
            colunas=request.data.get('colunas', 0),
            tiposala=request.data.get('tipo', 'Normal')
        )

        # Automatically generate seats (Lugares) for the room
        filas_count = int(request.data.get('filas', 0))
        colunas_count = int(request.data.get('colunas', 0))

        if filas_count > 0 and colunas_count > 0:
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            lugares = []
            for f in range(filas_count):
                fila_label = alphabet[f] if f < len(alphabet) else f"R{f}"
                for c in range(1, colunas_count + 1):
                    lugares.append(Lugares(
                        salaid=room,
                        fila=fila_label,
                        numero=c,
                        tipolugar='Normal'
                    ))
            Lugares.objects.bulk_create(lugares)

        log_action(request.user, 'create_room', 'Salas', room.salaid,
                   {"cinema": cinema.nomecinema, "nome": room.nomesala})
        return Response({"message": "Room and seats created successfully", "id": room.salaid},
                        status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_delete_movie_api(request, movie_id):
    """
    API to delete a movie (Admin only)
    """
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    try:
        movie = Filmes.objects.get(pk=movie_id)
        # Check for sessions
        if movie.sessoes.count() > 0:
            return Response({"error": "Cannot delete movie with active sessions"}, status=status.HTTP_400_BAD_REQUEST)

        movie.delete()
        log_action(request.user, 'delete_movie', 'Filmes', movie_id, {})
        return Response({"message": "Movie deleted successfully"})
    except Filmes.DoesNotExist:
        return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def criar_sessao_api(request):
    """
    API endpoint to create a new session (Admin only)
    """
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        return Response({"message": "Use POST to create a session", "user": request.user.username})

    serializer = SessaoCreateSerializer(data=request.data)
    if serializer.is_valid():
        sessao = serializer.save()

        # Logic: If the movie was "global" (no cinema), assign it to this session's cinema
        movie = sessao.filmeid
        room = sessao.salaid
        if movie and room and not movie.cinemaid:
            movie.cinemaid = room.cinemaid
            movie.save()

        # Initialize seats for the session
        try:
            sala = sessao.salaid
            lugares = Lugares.objects.filter(salaid=sala)
            lugares_sessao = [
                LugaresSessao(
                    lugarid=lugar,
                    sessaoid=sessao,
                    estado='Livre'
                ) for lugar in lugares
            ]
            LugaresSessao.objects.bulk_create(lugares_sessao)
        except Exception as e:
            # If seat generation fails, we might want to warn or rollback
            pass

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def deletar_sessao_api(request, sessaoid):
    """
    API endpoint to delete a session (Admin only)
    """
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    try:
        sessao = Sessoes.objects.get(pk=sessaoid)

        # Check for sold tickets (Bilhetes)
        if sessao.bilhetes.count() > 0:
            return Response({"error": "Cannot delete session with sold tickets"}, status=status.HTTP_400_BAD_REQUEST)

        # Clean up LugaresSessao
        LugaresSessao.objects.filter(sessaoid=sessao).delete()

        sessao.delete()
        return Response({"message": "Session deleted successfully"}, status=status.HTTP_200_OK)
    except Sessoes.DoesNotExist:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def bilhetes_sessao_api(request, sessaoid):
    """
    API to list all tickets for a session (Admin)
    """
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    bilhetes = Bilhetes.objects.filter(sessaoid=sessaoid).select_related('lugarid')
    data = []
    for b in bilhetes:
        try:
            linha = VendaLinhas.objects.filter(bilheteid=b).select_related('vendaid__clienteid').first()
            if linha and linha.vendaid:
                cliente = linha.vendaid.clienteid
                cliente_info = f"{cliente.nomecliente}" if cliente else "Unknown"
                venda_id = linha.vendaid.vendaid
            else:
                cliente_info = "N/A"
                venda_id = None
        except Exception:
            cliente_info = "Error"
            venda_id = None

        data.append({
            "bilheteid": b.bilheteid,
            "lugar": f"{b.lugarid.fila}{b.lugarid.numero}",
            "cliente": cliente_info,
            "venda_id": venda_id,
            "preco": b.precobilhete
        })
    return Response(data)


@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def cancelar_bilhete_api(request, bilheteid):
    """
    API to cancel a ticket (Admin)
    """
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    try:
        with transaction.atomic():
            bilhete = Bilhetes.objects.get(pk=bilheteid)
            lugar = bilhete.lugarid
            sessao = bilhete.sessaoid

            # 1. Update LugaresSessao to Livre
            try:
                ls = LugaresSessao.objects.get(lugarid=lugar, sessaoid=sessao)
                ls.estado = 'Livre'
                ls.save()
            except LugaresSessao.DoesNotExist:
                pass

            # 2. Delete VendaLinha
            VendaLinhas.objects.filter(bilheteid=bilhete).delete()

            # 3. Delete Bilhete
            bilhete.delete()

            return Response({"message": "Ticket cancelled successfully"})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def fetch_movie_metadata_api(request):
    """
    API to fetch movie metadata from external source (OMDb)
    """
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    title = request.query_params.get('title')
    if not title:
        return Response({"error": "Title parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    data = fetch_movie_data(title)
    if "error" in data:
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    return Response(data)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def bilhete_digital_api(request, bilheteid):
    """
    API to generate digital ticket info using a DATABASE FUNCTION (PostgreSQL)
    to ensure data integrity as per project requirements.
    """
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            # Call the PostgreSQL function
            cursor.execute("SELECT * FROM fn_gerar_detalhes_bilhete(%s)", [bilheteid])
            row = cursor.fetchone()
            
            if not row:
                return Response({"error": "Bilhete não encontrado"}, status=status.HTTP_404_NOT_FOUND)
            
            # Map columns from the RETURNS TABLE definition:
            # (bilhete_id, titulo_filme, nome_cinema, nome_sala, lugar_fila, lugar_numero, data_hora_inicio, preco_pago, emissao)
            ticket_data = {
                "bilhete_id": row[0],
                "titulo": row[1],
                "cinema": row[2],
                "sala": row[3],
                "fila": row[4],
                "lugar": row[5],
                "inicio": row[6],
                "preco": float(row[7]) if row[7] is not None else 0.0,
                "emissao": row[8]
            }
            
            # Security check: Only the owner (or staff) can view the digital ticket
            try:
                ticket_obj = Bilhetes.objects.get(pk=bilheteid)
                venda_linha = VendaLinhas.objects.filter(bilheteid=ticket_obj).select_related('vendaid').first()
                
                if venda_linha:
                    venda = venda_linha.vendaid
                    client_user = None
                    try:
                        profile = ClienteProfile.objects.get(cliente_dados=venda.clienteid)
                        client_user = profile.user
                    except:
                        pass
                    
                    if not request.user.is_staff and client_user != request.user:
                        return Response({"error": "Não tem permissão para aceder a este bilhete"}, 
                                        status=status.HTTP_403_FORBIDDEN)
            except Bilhetes.DoesNotExist:
                pass # Already handled by SQL row check but for safety

            return Response(ticket_data)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
import json

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

from django.db import connections

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
    dob = request.data.get('datanascimento', '2000-01-01')

    dto = NovoClienteDTO(
        username=username,
        password=password,
        email=email,
        nome_completo=username,  # Usa username como nome inicial
        data_nascimento=dob
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
    """API endpoint to get all active products using v_produtos_vendidos view for ranking/data"""
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT produtoid FROM v_produtos_vendidos")
        ids = [row[0] for row in cursor.fetchall()]
    
    produtos = Produtos.objects.filter(pk__in=ids, ativo=True, stock__gt=0)
    serializer = ProdutosSerializer(produtos, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def comprar_produtos_api(request):
    """
    API to process a purchase of concession items using Stored Procedure
    """
    try:
        user = request.user
        items = request.data.get('items', [])  # List of {produtoid, quantidade}

        if not items:
            return Response({"error": "No items provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Client ID
        try:
            profile = ClienteProfile.objects.select_related('cliente_dados').get(user=user)
            cliente_id = profile.cliente_dados.clienteid
        except ClienteProfile.DoesNotExist:
            cliente = Clientes.objects.filter(nomecliente=user.username).first()
            if not cliente:
                cliente = Clientes.objects.create(
                    nomecliente=user.username, 
                    emailcliente=user.email,
                    datanascimento='2000-01-01'
                )
            cliente_id = cliente.clienteid

        # 2. Products JSON
        products_list = []
        for item in items:
            products_list.append({"id": item['produtoid'], "qtd": int(item['quantidade'])})
        
        products_json = json.dumps(products_list)

        # 3. Call Procedure
        from django.db import connection
        with connection.cursor() as cursor:
            params = [
                cliente_id, 
                None, 
                None, # No session
                None, # No seats
                products_json, 
                0 # Placeholder for INOUT p_vendaid
            ]
            cursor.execute(
                "CALL realizar_venda_unificada(%s, %s, %s, %s, %s, %s)", 
                params
            )
            result = cursor.fetchone()
            venda_id = result[0]

            log_action(user, 'buy_concessions_proc', 'Vendas', venda_id, {"proc": True})

            return Response({"message": "Purchase successful", "venda_id": venda_id},
                            status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def filmes_api(request):
    cinema_id = request.query_params.get('cinema')
    
    if request.user.is_staff:
        queryset = Filmes.objects.select_related('categoriaid', 'classificacaoetaria', 'cinemaid')
        if cinema_id:
            queryset = queryset.filter(cinemaid=cinema_id)
        filmes = queryset.all()
        serializer = FilmesSerializer(filmes, many=True)
        return Response(serializer.data)
    else:
        # Use v_filmes_em_exibicao for regular users
        from django.db import connection
        with connection.cursor() as cursor:
            sql = "SELECT * FROM v_filmes_em_exibicao"
            params = []
            if cinema_id:
                sql += " WHERE cinemaid = %s" # Note: check if cinemaid is in the view
                pass
            
            cursor.execute("SELECT filmeid FROM v_filmes_em_exibicao")
            ids = [row[0] for row in cursor.fetchall()]
            
        queryset = Filmes.objects.filter(pk__in=ids).select_related('categoriaid', 'classificacaoetaria', 'cinemaid')
        if cinema_id:
            queryset = queryset.filter(cinemaid=cinema_id)
        
        filmes = queryset.all()
        serializer = FilmesSerializer(filmes, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def cinemas_api(request):
    """API endpoint to get all cinemas using the v_cinemas_resumo view"""
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM v_cinemas_resumo")
        columns = [col[0] for col in cursor.description]
        results = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    return Response(results)


@api_view(['GET'])
def salas_api(request):
    salas = Salas.objects.all()
    serializer = SalasSerializer(salas, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def sessoes_por_filme_api(request, filmeid):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT sessaoid FROM fn_obter_sessoes_ativas_por_filme(%s)", [filmeid])
            rows = cursor.fetchall()
            ids = [row[0] for row in rows]
            
        sessoes = Sessoes.objects.filter(pk__in=ids).select_related('salaid__cinemaid').order_by('inicio')
        serializer = SessoesSerializer(sessoes, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def lista_sessoes_api(request):
    """
    List sessions grouped by 'ativas' and 'terminadas'.
    High performance using JSON aggregation in PostgreSQL.
    """
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT fn_listar_sessoes_agrupadas()")
            data = cursor.fetchone()[0]

        return Response(data)

    except Exception as e:
        return Response({"error": "Erro interno: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    API to process a unified purchase (tickets and/or concessions) using Stored Procedure
    """
    try:
        user = request.user
        data = request.data
        sessaoid = data.get('sessaoid')
        lugares_ids = data.get('lugares_ids', [])
        products_raw = data.get('products', [])

        if not lugares_ids and not products_raw:
            return Response({"error": "Empty cart"}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare data for Procedure
        # 1. Client ID
        try:
            profile = ClienteProfile.objects.select_related('cliente_dados').get(user=user)
            cliente_id = profile.cliente_dados.clienteid
        except ClienteProfile.DoesNotExist:
            # Fallback for admin/legacy
            cliente = Clientes.objects.filter(nomecliente=user.username).first()
            if not cliente:
                # Need to create it? Or fail. Ideally create.
                cliente = Clientes.objects.create(
                    nomecliente=user.username, 
                    emailcliente=user.email,
                    datanascimento='2000-01-01'
                )
            cliente_id = cliente.clienteid

        # 2. Products JSON
        products_list = []
        for p in products_raw:
            products_list.append({"id": p['produtoid'], "qtd": int(p['quantidade'])})
        
        products_json = json.dumps(products_list)
        lugares_json = json.dumps(lugares_ids)

        # 3. Call Procedure
        from django.db import connection
        with connection.cursor() as cursor:
            params = [
                cliente_id, 
                None, # Funcionario ID (optional/null for online sales)
                sessaoid if sessaoid else None, 
                lugares_json, 
                products_json, 
                0 # Placeholder for INOUT p_vendaid
            ]
            
            # Use CALL explicitly for Procedures
            cursor.execute(
                "CALL realizar_venda_unificada(%s, %s, %s, %s, %s, %s)", 
                params
            )
            result = cursor.fetchone()
            venda_id = result[0]

            log_action(user, 'unified_purchase_proc', 'Vendas', venda_id, {"proc": True})

            return Response({"message": "Purchase successful", "venda_id": venda_id},
                            status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def minhas_vendas_api(request):
    try:
        # 1. Get client ID
        try:
            profile = ClienteProfile.objects.select_related('cliente_dados').get(user=request.user)
            cliente_id = profile.cliente_dados.clienteid
        except ClienteProfile.DoesNotExist:
            # If no client profile, return empty list
            return Response([])

        # 2. Execute function in database
        with connection.cursor() as cursor:
            cursor.execute("SELECT api_obter_historico_vendas(%s)", [cliente_id])
            result = cursor.fetchone()[0]

        return Response(result)

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

        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("CALL inserir_avaliacao(%s, %s, %s, %s, %s, %s)", [
                    venda.vendaid,
                    titulo,
                    int(nota_cinema) if nota_cinema is not None else None,
                    int(nota_filme) if nota_filme is not None else None,
                    int(nota_funcionario) if nota_funcionario is not None else None,
                    comentario
                ])
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        avaliacao = Avaliacoes.objects.get(venda=venda)

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

    try:
        with connections['admin'].cursor() as cursor:
            # Uses the simplified view created in SQL
            cursor.execute("SELECT * FROM v_avaliacoes_cliente")
            
            # Map columns to keys automatically
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            mapped_data = []
            for row in data:
                mapped_data.append({
                    "id": row['avaliacaoid'],
                    "venda_id": row['vendaid'],
                    "cliente": row['cliente_nome'],
                    "titulo": row['tituloavaliacao'],
                    "nota_cinema": row['avaliacaocinema'],
                    "nota_filme": row['avaliacaofilme'],
                    "nota_funcionario": row['avaliacaofuncionario'],
                    "comentario": row['comentario']
                })
                
        return Response(mapped_data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_funcionarios_api(request):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        with connections['admin'].cursor() as cursor:
            cursor.execute("SELECT * FROM mv_funcionarios_top")
            columns = [col[0] for col in cursor.description]
            raw_data = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
            
            # Map to frontend expected format
            data = []
            for item in raw_data:
                data.append({
                    "id": item['funcionarioid'],
                    "nome": item['nomefuncionario'],
                    "cargo": item['cargo'],
                    "cinema": item['nomecinema'],
                    "salario": item.get('salario', 0), # Added to MV
                    "media_avaliacao": item.get('media_avaliacao'),
                    "total_vendas": item.get('total_vendas'),
                    "total_faturado": item.get('total_faturado')
                })
                
        return Response(data)

    if request.method == 'POST':
        try:
            data = request.data

            cinema_id = data.get('cinemaid') if data.get('cinemaid') else None
            salario = data.get('salario') if data.get('salario') else 0

            with connections['admin'].cursor() as cursor:
                cursor.execute("CALL inserir_funcionario(%s, %s, %s, %s, %s, %s, %s)", [
                    data.get('nome'),
                    data.get('email'),
                    data.get('telefone', ''),
                    data.get('cargo'),
                    salario,
                    cinema_id,
                    None
                ])
                
                novo_id = cursor.fetchone()[0]

            return Response({
                "message": "Funcionário criado com sucesso", 
                "id": novo_id
            }, status=status.HTTP_201_CREATED)

        except DatabaseError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({"error": "Erro interno: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_create_produto_api(request):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    try:
        with connections['admin'].cursor() as cursor:
            cursor.execute("CALL inserir_produto(%s, %s, %s, %s)", [
                request.data.get('nome'),
                float(request.data.get('preco')),
                int(request.data.get('stock', 0)),
                True
            ])
        
        p = Produtos.objects.using('admin').get(nomeproduto=request.data.get('nome'))
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
        funcionario = Funcionarios.objects.using('admin').get(pk=pk)
        if request.method == 'DELETE':
            funcionario.delete(using='admin')
            return Response({"message": "Eliminado"})

        # Update
        funcionario.nomefuncionario = request.data.get('nome', funcionario.nomefuncionario)
        funcionario.cargo = request.data.get('cargo', funcionario.cargo)
        funcionario.salario = request.data.get('salario', funcionario.salario)
        funcionario.save(using='admin')
        return Response({"message": "Atualizado"})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_clientes_api(request):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    # GET: Listar Clientes (usando View)
    if request.method == 'GET':
        try:
            with connections['admin'].cursor() as cursor:
                cursor.execute("SELECT clienteid, nomecliente, emailcliente, telefonecliente, nif FROM v_clientes_global")
                rows = cursor.fetchall()
                
            data = [{
                "id": row[0],
                "nome": row[1],
                "email": row[2],
                "telefone": row[3],
                "nif": row[4]
            } for row in rows]
            return Response(data)
        except Exception as e:
             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # POST: Criar Cliente (usando Procedure)
    if request.method == 'POST':
        try:
            data = request.data
            with connections['admin'].cursor() as cursor:
                cursor.execute("CALL inserir_cliente(%s, %s, %s, %s, %s, %s, %s, %s)", [
                    data.get('nome'),
                    data.get('email'),
                    data.get('telefone', ''),
                    data.get('datanascimento') if data.get('datanascimento') else None,
                    data.get('morada', ''),
                    data.get('codigopostal', ''),
                    data.get('localidade', ''),
                    data.get('nif')
                ])
            
            # Fetch back to return ID (Optional but good for frontend)
            c = Clientes.objects.using('admin').filter(emailcliente=data.get('email')).first()
            return Response({"id": c.clienteid if c else None, "message": "Cliente criado"}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_cliente_detail_api(request, pk):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    try:
        cliente = Clientes.objects.using('admin').get(pk=pk)
        if request.method == 'DELETE':
            cliente.delete(using='admin')
            return Response({"message": "Eliminado"})
        cliente.nomecliente = request.data.get('nome', cliente.nomecliente)
        cliente.emailcliente = request.data.get('email', cliente.emailcliente)
        cliente.save(using='admin')
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
        produto = Produtos.objects.using('admin').get(pk=pk)
        if request.method == 'DELETE':
            produto.ativo = False
            produto.save(using='admin')
            return Response({"message": "Desativado"})

        # Support relative stock update if 'stock_change' is provided
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

        produto.save(using='admin')
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

        with connections['admin'].cursor() as cursor:
            cursor.execute("CALL inserir_filme(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [
                categoria.categoriaid,
                cinema.cinemaid if cinema else None,
                request.data.get('titulo'),
                request.data.get('datalancamento'),
                request.data.get('duracao'),
                request.data.get('produtora'),
                request.data.get('fimexebicao'),
                request.data.get('idioma', 'PT'),
                request.data.get('sinopse', ''),
                classificacao.classificacaoid,
                request.data.get('ranking', 0.0),
                request.data.get('cartaz_url'),
                None # Placeholder for OUT p_novo_id
            ])
            movie_id = cursor.fetchone()[0]
        
        # Log action using the returned ID
        log_action(request.user, 'create_movie', 'Filmes', movie_id, {"titulo": request.data.get('titulo')})

        return Response({"message": "Movie created successfully", "id": movie_id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_vendas_api(request):
    """
    API to list every sale in the system (Admin only) - Otimizado
    """
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    try:
        with connections['admin'].cursor() as cursor:
            cursor.execute("SELECT fn_listar_todas_vendas()")
            data = cursor.fetchone()[0]
        return Response(data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        with connections['admin'].cursor() as cursor:
            cursor.execute("CALL inserir_cinema(%s, %s, %s, %s, %s, %s, %s, %s)", [
                request.data.get('nome'),
                request.data.get('email', ''),
                request.data.get('telefone', ''),
                request.data.get('morada', ''),
                request.data.get('codigo_postal', ''),
                request.data.get('localidade'),
        0.0,
                None # Placeholder for OUT p_novo_id
            ])
            cinema_id = cursor.fetchone()[0]
        
        log_action(request.user, 'create_cinema', 'Cinemas', cinema_id, {"nome": request.data.get('nome')})
        return Response({"message": "Cinema created successfully", "id": cinema_id},
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
        cinema = Cinemas.objects.using('admin').get(pk=cinema_id)
        
        with connections['admin'].cursor() as cursor:
            cursor.execute("CALL inserir_sala(%s, %s, %s, %s, %s)", [
                cinema.cinemaid,
                request.data.get('nome'),
                int(request.data.get('filas', 0)),
                int(request.data.get('colunas', 0)),
                request.data.get('tipo', 'Normal')
            ])
            
        # Fetch the created room
        room = Salas.objects.using('admin').filter(cinemaid=cinema, nomesala=request.data.get('nome')).last()

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
        movie = Filmes.objects.using('admin').get(pk=movie_id)
        # Check for sessions
        if movie.sessoes.count() > 0:
            return Response({"error": "Cannot delete movie with active sessions"}, status=status.HTTP_400_BAD_REQUEST)

        movie.delete(using='admin')
        log_action(request.user, 'delete_movie', 'Filmes', movie_id, {})
        return Response({"message": "Movie deleted successfully"})
    except Filmes.DoesNotExist:
        return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def criar_sessao_api(request):
    # 1. Check permissions (Admin only)
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    try:
        data = request.data
        
        # 2. Basic validation for required fields
        required_fields = ['salaid', 'filmeid', 'inicio', 'fim']
        if not all(field in data for field in required_fields):
            return Response({"error": "Missing required fields (salaid, filmeid, inicio, fim)."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Prepare parameters (Order must match SQL Procedure)
        params = [
            data['salaid'],
            data['filmeid'],
            data['inicio'],               # Format: 'YYYY-MM-DD HH:MM:SS'
            data['fim'],
            data.get('versao', '2D'),     # Default value
            data.get('estadosessao', 'Agendada'),
            data.get('precosessao', 0),
            None                          # Placeholder for OUT parameter (p_novo_id)
        ]

        # 4. Execute Stored Procedure
        with connections['admin'].cursor() as cursor:
            # 8 parameters: 7 IN + 1 OUT
            cursor.execute("CALL inserir_sessao(%s, %s, %s, %s, %s, %s, %s, %s)", params)
            
            # Fetch the generated ID from the OUT parameter
            new_id = cursor.fetchone()[0]

        return Response({
            "message": "Session created successfully.", 
            "id": new_id
        }, status=status.HTTP_201_CREATED)

    except DatabaseError as e:
        # 5. Handle DB errors (Trigger validations like overlaps or capacity)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Handle generic server errors
        return Response({"error": "Internal Error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        sessao = Sessoes.objects.using('admin').get(pk=sessaoid)

        # Check for sold tickets (Bilhetes)
        if sessao.bilhetes.count() > 0:
            return Response({"error": "Cannot delete session with sold tickets"}, status=status.HTTP_400_BAD_REQUEST)

        # Clean up LugaresSessao
        LugaresSessao.objects.using('admin').filter(sessaoid=sessao).delete()

        sessao.delete(using='admin')
        return Response({"message": "Session deleted successfully"}, status=status.HTTP_200_OK)
    except Sessoes.DoesNotExist:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def atualizar_sessao_api(request, sessaoid):
    """
    API endpoint to update session state (Admin only)
    """
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    novo_estado = request.data.get('estadosessao')
    if not novo_estado:
        return Response({"error": "State is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with connections['admin'].cursor() as cursor:
            cursor.execute("CALL alterar_estado_sessao(%s, %s)", [sessaoid, novo_estado])
            
        return Response({"message": "Session updated successfully"})
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

    bilhetes = Bilhetes.objects.using('admin').filter(sessaoid=sessaoid).select_related('lugarid')
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
        with transaction.atomic(using='admin'):
            bilhete = Bilhetes.objects.using('admin').get(pk=bilheteid)
            lugar = bilhete.lugarid
            sessao = bilhete.sessaoid

            # 1. Update LugaresSessao to Livre
            try:
                ls = LugaresSessao.objects.using('admin').get(lugarid=lugar, sessaoid=sessao)
                ls.estado = 'Livre'
                ls.save(using='admin')
            except LugaresSessao.DoesNotExist:
                pass

            # 2. Delete VendaLinha
            VendaLinhas.objects.using('admin').filter(bilheteid=bilhete).delete()

            # 3. Delete Bilhete
            bilhete.delete(using='admin')

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
            return Response({"error": "Bilhete não encontrado"}, status=status.HTTP_404_NOT_FOUND)

        with connection.cursor() as cursor:
            # Call the PostgreSQL function which returns a JSON object
            cursor.execute("SELECT exportar_bilhete_pdf(%s)", [bilheteid])
            row = cursor.fetchone()
            
            if not row or row[0] is None:
                return Response({"error": "Erro ao gerar dados do bilhete"}, status=status.HTTP_404_NOT_FOUND)
            
            data = row[0]
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    return Response({"error": "Erro ao processar dados do bilhete"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(data)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def fatura_digital_api(request, vendaid):
    """
    API to generate digital invoice info using a DATABASE FUNCTION (PostgreSQL)
    """
    from django.db import connection
    
    try:
        # Security check: Only the owner (or staff) can view the invoice
        try:
            venda = Vendas.objects.get(pk=vendaid)
            client_user = None
            try:
                profile = ClienteProfile.objects.get(cliente_dados=venda.clienteid)
                client_user = profile.user
            except:
                pass
            
            if not request.user.is_staff and client_user != request.user:
                return Response({"error": "Não tem permissão para aceder a esta fatura"}, 
                                status=status.HTTP_403_FORBIDDEN)
        except Vendas.DoesNotExist:
            return Response({"error": "Venda não encontrada"}, status=status.HTTP_404_NOT_FOUND)

        with connection.cursor() as cursor:
            # Call the PostgreSQL function which returns a JSON object
            cursor.execute("SELECT exportar_fatura_pdf(%s)", [vendaid])
            row = cursor.fetchone()
            
            if not row or row[0] is None:
                return Response({"error": "Erro ao gerar dados da fatura"}, status=status.HTTP_404_NOT_FOUND)
            
            data = row[0]
            if isinstance(data, str):
                data = json.loads(data)

            return Response(data)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def exportar_faturas_dia_api(request):
    """
    API to export all invoices for a given day using SQL function.
    Only for staff.
    """
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    from django.db import connection
    from django.utils.dateparse import parse_date
    
    data_str = request.query_params.get('data')
    target_date = parse_date(data_str) if data_str else timezone.now().date()

    try:
        with connections['admin'].cursor() as cursor:
            cursor.execute("SELECT exportar_faturas_por_data(%s)", [target_date])
            row = cursor.fetchone()
            
            if not row or row[0] is None:
                return Response([], status=status.HTTP_200_OK) # Empty list if no invoices
            
            data = row[0]
            if isinstance(data, str):
                data = json.loads(data)

            return Response(data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def categorias_api(request):
    """
    API to list all categories
    """
    categorias = Categorias.objects.all().order_by('categoriaid')
    data = [{"id": c.categoriaid, "name": c.nomecategoria} for c in categorias]
    return Response(data)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_create_categoria_api(request):
    """
    API to create a category using Stored Procedure.
    """
    # 1. Check permissions
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    try:
        nome = request.data.get('nome')

        # 2. Call Stored Procedure
        with connections['admin'].cursor() as cursor:
            cursor.execute("CALL inserir_categoria(%s, %s)", [nome, None])
            new_id = cursor.fetchone()[0]

        # 3. Log action
        log_action(request.user, 'create_category', 'Categorias', new_id, {"nome": nome})
        return Response({
            "message": "Category created successfully", 
            "id": new_id
        }, status=status.HTTP_201_CREATED)

    except DatabaseError as e:
        # Handles "Name required" or "Duplicate category" errors from SQL
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": "Internal Error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_delete_categoria_api(request, pk):
    """
    API to delete a category (Admin only)
    """
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    try:
        cat = Categorias.objects.using('admin').get(pk=pk)
        # Check constraints (filmes)
        if cat.filmes.count() > 0:
            return Response({"error": "Cannot delete category with related movies"}, status=status.HTTP_400_BAD_REQUEST)

        cat.delete(using='admin')
        log_action(request.user, 'delete_category', 'Categorias', pk, {})
        return Response({"message": "Category deleted"})
    except Categorias.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


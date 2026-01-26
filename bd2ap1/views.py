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

# Model Imports
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

from clientes.models import ClienteProfile
from clientes.core.services import ClienteService
from clientes.core.dtos import NovoClienteDTO
from clientes.core.exceptions import ClienteServiceException

from django.db import connections

def index(request):
    return render(request, 'core/index.html')

def home(request):
    return render(request, 'core/index.html')

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object

        try:
            if not ClienteProfile.objects.filter(user=user).exists():
                email = form.cleaned_data.get('email', '')
                cliente = Clientes.objects.create(
                    nomecliente=user.username,
                    emailcliente=email
                )
                ClienteProfile.objects.create(user=user, cliente_dados=cliente)

                log_action(user, 'signup_legacy', 'User', user.id, {"email": email})
        except Exception:
            pass

        return response

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    """
    Endpoint for React Login.
    Returns JSON response and sets the Session Cookie.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)  # Creates the sessionid cookie
        log_action(user, 'login_api', 'User', user.id, {"status": "success"})

        # Check if user is staff to determine if the admin panel should be shown on frontend
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
    Endpoint for Registration via React (Uses Clean Architecture)
    """
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    dob = request.data.get('datanascimento', '2000-01-01')

    dto = NovoClienteDTO(
        username=username,
        password=password,
        email=email,
        nome_completo=username,  # Uses username as default name
        data_nascimento=dob
    )

    service = ClienteService()
    try:
        # Service creates User + Client + Profile in a secure transaction
        profile = service.registrar_novo_cliente(dto)

        log_action(profile.user, 'signup_api', 'User', profile.user.id, {"email": email})

        # Auto-login after registration
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
    """ Endpoint for React to validate the current session """
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
    """ API to update Email, NIF and Phone (Username is read-only) """
    try:
        user_id = request.user.id
        
        # 1. Capture all input fields
        email = request.data.get('email')
        nif = request.data.get('nif')
        telefone = request.data.get('telefone')
        codigo_postal = request.data.get('codigo_postal')

        # Simple validation
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Execute SQL function with the provided parameters
        with connections['admin'].cursor() as cursor:
            cursor.execute(
                "SELECT fn_atualizar_perfil_user(%s, %s, %s, %s, %s)", 
                [user_id, email, nif, telefone, codigo_postal]
            )
            result = cursor.fetchone()[0]

        if result.get('status') == 'error':
            return Response({"error": result.get('message')}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
#  Business Logic API Endpoints (Sales, Movies, etc.)
# ==============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def produtos_api(request):
    try:
        with connections['admin'].cursor() as cursor:
            cursor.execute("SELECT fn_obter_produtos_api()")
            result = cursor.fetchone()[0]

        return Response(result)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def filmes_api(request):
    try:
        cinema_param = request.query_params.get('cinema')
        cinema_id = int(cinema_param) if cinema_param and cinema_param.isdigit() else None

        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT fn_listar_filmes_api(%s)", [cinema_id])
            result = cursor.fetchone()[0]
            
        return Response(result)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def cinemas_api(request):
    """API endpoint to get all cinemas using the v_cinemas_resumo view"""
    from django.db import connection
    with connections['default'].cursor() as cursor:
        cursor.execute("SELECT * FROM v_cinemas_resumo")
        columns = [col[0] for col in cursor.description]
        results = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    return Response(results)


@api_view(['GET'])
def salas_api(request):
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT fn_listar_salas_api()")
            result = cursor.fetchone()[0]
            
        return Response(result)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def sessoes_por_filme_api(request, filmeid):
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT fn_listar_sessoes_por_filme(%s)", [filmeid])
            result = cursor.fetchone()[0]
            
        return Response(result)
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def lista_sessoes_api(request):
    try:
        with connections['admin'].cursor() as cursor:
            cursor.execute("SELECT fn_listar_sessoes_agrupadas()")
            data = cursor.fetchone()[0]
        return Response(data if data else {})

    except Exception as e:
        return Response(
            {"error": "Internal Error: " + str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def lugares_sessao_api(request, sessaoid):
    """
    List places of a session. If the places are not created, create them.
    """
    try:
        with connections['admin'].cursor() as cursor:
            cursor.execute("SELECT fn_listar_lugares_sessao(%s)", [sessaoid])
            result = cursor.fetchone()[0]

        if isinstance(result, dict) and result.get('error'):
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        return Response(result)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def comprar_produtos_api(request):
    try:
        user = request.user
        items = request.data.get('items', []) 
        if not items:
            return Response({"error": "The snack cart is empty."}, status=400)

        products_list = [{"id": int(i['produtoid']), "qtd": int(i['quantidade'])} for i in items]
        products_json = json.dumps(products_list)

        with connections['admin'].cursor() as cursor:
            cursor.execute("""
                SELECT fn_realizar_venda_unificada(
                    %s, %s, %s,   -- User ID, Name, Email
                    NULL,         -- Session (NULL)
                    NULL,         -- Seats (NULL)
                    %s::jsonb     -- Products JSON
                )
            """, [user.id, user.username, user.email, products_json])
            
            venda_id = cursor.fetchone()[0]

        return Response({"message": "Snack purchase successful!", "venda_id": venda_id}, status=201)

    except Exception as e:
        print(f"BAR ERROR: {e}")
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def criar_venda_api(request):
    try:
        user = request.user
        data = request.data
        
        sessaoid = data.get('sessaoid')
        lugares_ids = data.get('lugares_ids', [])
        products_raw = data.get('items') or data.get('products') or []

        if not lugares_ids and not products_raw:
            return Response({"error": "The cart is empty. Please select tickets or snacks."}, status=400)

        lugares_json = json.dumps(lugares_ids)
        
        products_list = [{"id": int(p['produtoid']), "qtd": int(p['quantidade'])} for p in products_raw]
        products_json = json.dumps(products_list)

        with connections['admin'].cursor() as cursor:
            cursor.execute("""
                SELECT fn_realizar_venda_unificada(
                    %s, %s, %s,   -- User ID, Name, Email
                    %s,           -- Session ID
                    %s::jsonb,    -- Seats JSON
                    %s::jsonb     -- Products JSON
                )
            """, [
                user.id, user.username, user.email,
                sessaoid,
                lugares_json,
                products_json
            ])
            
            venda_id = cursor.fetchone()[0]

        return Response({"message": "Tickets issued successfully!", "venda_id": venda_id}, status=201)

    except Exception as e:
        print(f"TICKETING ERROR: {e}")
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def minhas_vendas_api(request):
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute("""
                SELECT fn_obter_historico_vendas_cliente(
                    fn_resolver_cliente_id(%s)
                )
            """, [request.user.username])
            
            result = cursor.fetchone()[0]

        return Response(result if result else [])

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
        venda_id = request.data.get('venda_id')
        
        with connections['default'].cursor() as cursor:
            # 1. Ownership Verification (Directly in SQL)
            # Check if the sale belongs to the request.user username
            cursor.execute("""
                SELECT 1 FROM vendas v 
                JOIN clientes c ON v.clienteid = c.clienteid 
                WHERE v.vendaid = %s AND c.nomecliente = %s
            """, [venda_id, request.user.username])
            
            if not cursor.fetchone():
                return Response({"error": "You do not have permission to rate this sale"}, status=403)

            # 2. Call Stored Procedure
            cursor.execute("CALL inserir_avaliacao(%s, %s, %s, %s, %s, %s)", [
                venda_id,
                request.data.get('titulo', 'Purchase Review'),
                request.data.get('nota_cinema'),
                request.data.get('nota_filme'),
                request.data.get('nota_funcionario'),
                request.data.get('comentario', '')
            ])

        return Response({"message": "Review submitted successfully"}, status=201)

    except Exception as e:
        # Catch Procedure exceptions (e.g. 'Sale not finished')
        return Response({"error": str(e)}, status=400)


# ==============================================================================
#  Admin API (Staff Only)
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
                    "salario": item.get('salario', 0), # Added to Materialized View
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
                "message": "Employee created successfully", 
                "id": novo_id
            }, status=status.HTTP_201_CREATED)

        except DatabaseError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({"error": "Internal Error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        return Response(status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_funcionario_detail_api(request, pk):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    try:
        with connections['admin'].cursor() as cursor:
            # Delete Action
            if request.method == 'DELETE':
                cursor.execute("CALL proc_eliminar_funcionario(%s)", [pk])
                return Response({"message": "Employee deleted successfully"})

            # Update Action
            # Extract values from request.data
            cursor.execute("CALL proc_editar_funcionario(%s, %s, %s, %s)", [
                pk,
                request.data.get('nome'),
                request.data.get('cargo'),
                request.data.get('salario')
            ])
            
            return Response({"message": "Employee details updated"})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_clientes_api(request):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    # GET: List Clients (using View)
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

    # POST: Create Client (using Procedure)
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
            
            return Response({"message": "Client created"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_cliente_detail_api(request, pk):
    """
    Eliminate or update a client via SQL procedures.
    """
    try:
        with connections['admin'].cursor() as cursor:
            # 1. Delete Client
            if request.method == 'DELETE':
                cursor.execute("CALL eliminar_cliente(%s)", [pk])
                return Response({"message": "Deleted successfully"})

            # 2. Update Client
            cursor.execute("CALL editar_cliente(%s, %s, %s)", [
                pk,
                request.data.get('nome'),
                request.data.get('email')
            ])
            
            return Response({"message": "Client details updated"})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_produto_detail_api(request, pk):
    try:
        with connections['admin'].cursor() as cursor:
            # Action 1: Soft Delete
            if request.method == 'DELETE':
                cursor.execute("CALL desativar_produto(%s)", [pk])
                return Response({"message": "Product deactivated"})

            # Action 2: Stock Adjustment
            stock_change = request.data.get('stock_change')
            if stock_change is not None:
                cursor.execute("CALL ajustar_stock_produto(%s, %s, %s)", [pk, int(stock_change), None])
                novo_stock = cursor.fetchone()[0]
                return Response({"message": "Stock adjusted", "new_stock": novo_stock})

            # Action 3: Complete Edit
            cursor.execute("CALL editar_produto(%s, %s, %s, %s)", [
                pk,
                request.data.get('nome'),
                request.data.get('preco'),
                request.data.get('stock')
            ])
            return Response({"message": "Data updated successfully"})

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
        categoria_id = request.data.get('categoriaid')
        classificacao_id = request.data.get('classificacaoid', 1)
        cinema_id = request.data.get('cinemaid')

        with connections['admin'].cursor() as cursor:
            cursor.execute("""
                CALL inserir_filme(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                categoria_id,
                cinema_id,
                request.data.get('titulo'),
                request.data.get('datalancamento'),
                request.data.get('duracao'),
                request.data.get('produtora'),
                request.data.get('fimexebicao'),
                request.data.get('idioma', 'PT'),
                request.data.get('sinopse', ''),
                classificacao_id,
                request.data.get('ranking', 0.0),
                request.data.get('cartaz_url')
            ])
            movie_id = cursor.fetchone()[0]
        
        return Response({
            "message": "Movie created successfully", 
            "id": movie_id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def admin_vendas_api(request):
    """
    API to list every sale in the system (Admin only) - Optimized
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
        nome = request.data.get('nome')
        filas = int(request.data.get('filas', 0))
        colunas = int(request.data.get('colunas', 0))
        tipo = request.data.get('tipo', 'Normal')

        with connections['admin'].cursor() as cursor:
            cursor.execute("CALL inserir_sala(%s, %s, %s, %s, %s, %s)", [
                int(cinema_id),
                nome,
                filas,
                colunas,
                tipo,
                None 
            ])   
            nova_sala_id = cursor.fetchone()[0]

        return Response({
            "message": "Room and seats created successfully!",
            "id": nova_sala_id
        }, status=status.HTTP_201_CREATED)

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
        with connections['admin'].cursor() as cursor:
            cursor.execute("CALL eliminar_filme(%s)", [movie_id])
        
        log_action(request.user, 'delete_movie', 'Filmes', movie_id, {})
        return Response({"message": "Movie deleted successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        erro_msg = str(e)
        
        # Error mapping from SQL to HTTP Status Codes
        if 'Filme não encontrado' in erro_msg:
            return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)
            
        if 'existem sessões associadas' in erro_msg:
            return Response(
                {"error": "Cannot delete movie with active sessions"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response({"error": erro_msg}, status=status.HTTP_400_BAD_REQUEST)


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
        
        log_action(request.user, 'create_session', 'Sessões', new_id, {"filme": data['filmeid'], "sala": data['salaid']})

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
        with connections['admin'].cursor() as cursor:
            cursor.execute("CALL eliminar_sessao(%s)", [sessaoid])
        
        return Response({"message": "Session deleted successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        erro_msg = str(e)
        
        # Error mapping to keep the original logic
        if 'Sessão não encontrada' in erro_msg:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
            
        if 'existem bilhetes vendidos' in erro_msg:
            return Response({"error": "Cannot delete session with sold tickets"}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({"error": erro_msg}, status=status.HTTP_400_BAD_REQUEST)


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

    try:
        with connections['admin'].cursor() as cursor:
            cursor.execute("SELECT fn_listar_bilhetes_sessao_admin(%s)", [sessaoid])
            data = cursor.fetchone()[0]

        if isinstance(data, str):
            data = json.loads(data)

        return Response(data if data else [])

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def cancelar_bilhete_api(request, bilheteid):
    """
    API to cancel a ticket (Admin)
    """
    try:
        with connections['admin'].cursor() as cursor:
            # Call simplified procedure
            cursor.execute("CALL cancelar_bilhete(%s)", [bilheteid])
        
        return Response({"message": "Cancellation completed successfully."})
    except Exception as e:
        return Response({"error": str(e)}, status=400)


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
    try:
        with connections['default'].cursor() as cursor:            
            # 1. SECURITY VERIFICATION
            cursor.execute("SELECT user_id FROM v_bilhetes_seguranca WHERE bilheteid = %s", [bilheteid])
            
            row = cursor.fetchone()
            
            if not row:
                return Response({"error": "Ticket not found"}, status=404)
            
            owner_user_id = row[0]

            # Permission Verification (Staff or Owner)
            if not request.user.is_staff and owner_user_id != request.user.id:
                return Response({"error": "You do not have permission to access this ticket"}, status=403)

            # 2. RETRIEVE TICKET DATA (Calls SQL function)
            cursor.execute("SELECT exportar_bilhete_pdf(%s)", [bilheteid])
            result = cursor.fetchone()
            
            if not result or result[0] is None:
                return Response({"error": "Error generating ticket data"}, status=404)
            
            data = result[0]
            
            # Convert string to dict if necessary (depends on Postgres driver)
            if isinstance(data, str):
                data = json.loads(data)

            return Response(data)

    except Exception as e:
        # Log error in terminal for debugging
        print(f"Digital Ticket Error: {e}")
        return Response({"error": str(e)}, status=400)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def fatura_digital_api(request, vendaid):
    """
    API to generate digital invoice info using a DATABASE FUNCTION (PostgreSQL)
    """
    try:
        with connections['default'].cursor() as cursor:
            
            # 1. SECURITY VERIFICATION (Who owns this sale?)
            cursor.execute("SELECT user_id FROM v_vendas_users WHERE vendaid = %s", [vendaid])
            row = cursor.fetchone()

            if not row:
                return Response({"error": "Sale not found"}, status=status.HTTP_404_NOT_FOUND)
            
            owner_user_id = row[0]

            # Permission Logic:
            if not request.user.is_staff and owner_user_id != request.user.id:
                return Response(
                    {"error": "You do not have permission to view this invoice."}, 
                    status=status.HTTP_403_FORBIDDEN
                )

            # 2. RETRIEVE INVOICE DATA (SQL Function)
            cursor.execute("SELECT exportar_fatura_pdf(%s)", [vendaid])
            result = cursor.fetchone()
            
            if not result or result[0] is None:
                return Response({"error": "Invoice details unavailable"}, status=404)

            fatura_json = result[0]

            # Ensures it is sent as a JSON Object, not a String
            if isinstance(fatura_json, str):
                fatura_json = json.loads(fatura_json)

            return Response(fatura_json)

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
    try:
        with connections['admin'].cursor() as cursor:
            cursor.execute("SELECT fn_listar_categorias()")
            data = cursor.fetchone()[0]
            
        return Response(data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    try:
        with connections['admin'].cursor() as cursor:
            # Call Procedure. If it fails, it raises an error here.
            cursor.execute("CALL eliminar_categoria(%s)", [pk])
        
        # If we reached here, everything went well
        log_action(request.user, 'delete_category', 'Categorias', pk, {})
        return Response({"message": "Category deleted successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        erro_msg = str(e)
        
        # Map SQL errors to HTTP Status Codes
        if 'Categoria não encontrada' in erro_msg:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
            
        elif 'Existem filmes associados' in erro_msg:
            return Response(
                {"error": "Cannot delete category with related movies"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Generic error
        return Response({"error": erro_msg}, status=status.HTTP_400_BAD_REQUEST)
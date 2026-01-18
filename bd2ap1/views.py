from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework import status

from bd2ap1.mongo_logger import log_action
from .serializers import (
    FilmesSerializer, SessoesSerializer, LugaresSessaoSerializer, SessaoCreateSerializer,
    SalasSerializer, CinemasSerializer, ProdutosSerializer,
)
from .models import (
    Filmes, Sessoes, LugaresSessao, Vendas, VendaLinhas, Bilhetes, Clientes, Lugares, Salas, Cinemas, Produtos,
)
from clientes.models import ClienteProfile
from clientes.auth_forms import ClienteSignupForm
from clientes.core.dtos import NovoClienteDTO
from clientes.core.services import ClienteService

def index(request):
    return render(request, 'core/index.html')

def home(request):
    return render(request, 'core/index.html')

class SignUpView(generic.FormView):
    form_class = ClienteSignupForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        # Registra sempre como CLIENTE (não-admin)
        dto = NovoClienteDTO(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email'],
            nome_completo=form.cleaned_data['username'],
        )

        service = ClienteService()
        profile = service.registrar_novo_cliente(dto)

        # Após registar, redireciona para login (mantém comportamento atual)
        return super().form_valid(form)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
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
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            # cria também um Cliente (dados mínimos) + vínculo
            if not ClienteProfile.objects.filter(user=user).exists():
                cliente = Clientes.objects.create(
                    nomecliente=username,
                    emailcliente=email or '',
                )
                ClienteProfile.objects.create(user=user, cliente_dados=cliente)

        # Optional: Auto-login after signup
        login(request, user)
        return Response(
            {
                "message": "User created successfully",
                "username": user.username,
                "cliente_id": user.cliente_profile.cliente_dados_id if hasattr(user, 'cliente_profile') else None,
            },
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def logout_api(request):
    logout(request)
    return Response({"message": "Logout successful"})

@api_view(['GET'])
@permission_classes([AllowAny])
def whoami_api(request):
    return Response({
        "is_authenticated": request.user.is_authenticated,
        "username": request.user.username if request.user.is_authenticated else None,
        "is_staff": request.user.is_staff if request.user.is_authenticated else False,
        "session_key": request.session.session_key
    })

@api_view(['GET'])
def filmes_api(request):
    """
    API endpoint to get all movies in JSON format, optionally filtered by cinema
    """
    cinema_id = request.query_params.get('cinema')
    queryset = Filmes.objects.select_related('categoriaid', 'classificacaoetaria', 'cinemaid')
    
    if cinema_id:
        queryset = queryset.filter(cinemaid=cinema_id)
        
    filmes = queryset.all()
    serializer = FilmesSerializer(filmes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def cinemas_api(request):
    """
    API endpoint to get all cinemas in JSON format
    """
    cinemas = Cinemas.objects.all()
    serializer = CinemasSerializer(cinemas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def salas_api(request):
    """
    API endpoint to get all rooms
    """
    salas = Salas.objects.all()
    serializer = SalasSerializer(salas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def sessoes_por_filme_api(request, filmeid):
    """
    API endpoint to get sessions for a specific movie
    """
    try:
        sessoes = Sessoes.objects.filter(filmeid=filmeid).select_related('salaid__cinemaid').order_by('inicio')
        serializer = SessoesSerializer(sessoes, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(['GET'])
def lista_sessoes_api(request):
    """
    API endpoint to list all sessions (for admin)
    """
    sessoes = Sessoes.objects.select_related('filmeid', 'salaid').order_by('-inicio')
    serializer = SessoesSerializer(sessoes, many=True)
    return Response(serializer.data)

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
            
        # Clean up LugaresSessao (if using CASCADE it would be automatic, but let's be safe or if it's PROTECT)
        # LugaresSessao is PROTECT on sessao, so we must delete them first
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
    except Bilhetes.DoesNotExist:
        return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def lugares_sessao_api(request, sessaoid):
    """
    API endpoint to get seats for a session
    """
    try:
        # Get all seats for the session (LugaresSessao)
        # Assuming LugaresSessao are pre-generated. 
        # If not, we might need to get all Lugares for the room and left join with LugaresSessao.
        # For now, let's assume we can fetch what's in LugaresSessao.
        
        # Strategy: Get the session to find the room
        sessao = Sessoes.objects.get(pk=sessaoid)
        
        # Check if we have LugaresSessao records
        lugares_ocupados = LugaresSessao.objects.filter(sessaoid=sessaoid)
        
        if not lugares_ocupados.exists():
            # If no records exist yet, generate them from the room's seats
            sala = sessao.salaid
            if sala:
                lugares = Lugares.objects.filter(salaid=sala)
                lugares_sessao_novos = [
                    LugaresSessao(
                        lugarid=lugar,
                        sessaoid=sessao,
                        estado='Livre'
                    ) for lugar in lugares
                ]
                LugaresSessao.objects.bulk_create(lugares_sessao_novos)
                # Re-fetch the newly created seats
                lugares_ocupados = LugaresSessao.objects.filter(sessaoid=sessaoid)

        # Use the serializer which includes the Lugar details
        serializer = LugaresSessaoSerializer(lugares_ocupados, many=True)
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
    API to process a ticket sale
    """
    try:
        user = request.user
        data = request.data
        sessaoid = data.get('sessaoid')
        lugares_ids = data.get('lugares_ids') # List of lugarid or lugarsessaoid
        
        if not sessaoid or not lugares_ids:
            return Response({"error": "Missing session or seats data"}, status=status.HTTP_400_BAD_REQUEST)
            
        with transaction.atomic():
            # 1. Get/Create Client using Username as unique identifier
            # This prevents users with empty emails from sharing the same 'anonymous' client record
            cliente, created = Clientes.objects.get_or_create(
                nomecliente=user.username,
                defaults={'emailcliente': user.email}
            )
            
            # 2. Create Venda
            venda = Vendas.objects.create(
                clienteid=cliente,
                data=timezone.now().date(),
                estadovenda='Concluída',
                totalvenda=0 # Will update later
            )
            
            sessao = Sessoes.objects.get(pk=sessaoid)
            total = 0
            
            for ls_id in lugares_ids:
                # Assuming ls_id is lugarsessaoid
                ls = LugaresSessao.objects.select_related('lugarid').get(pk=ls_id)
                
                if ls.estado != 'Livre':
                    raise Exception(f"Lugar {ls.lugarid.fila}{ls.lugarid.numero} is not available")
                
                # Update status
                ls.estado = 'Ocupado'
                ls.save()
                
                # Create Bilhete
                price = sessao.precosessao or 10.00 # Fallback price
                bilhete = Bilhetes.objects.create(
                    lugarid=ls.lugarid,
                    sessaoid=sessao,
                    precobilhete=price,
                    emissao=timezone.now()
                )
                
                # Create VendaLinha
                VendaLinhas.objects.create(
                    vendaid=venda,
                    bilheteid=bilhete,
                    quantidade=1,
                    precolinha=price,
                    total_linha=price
                )
                
                total += price
                
            venda.totalvenda = total
            venda.save()
            
            return Response({"message": "Purchase successful", "venda_id": venda.vendaid}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def minhas_vendas_api(request):
    user = request.user
    # Find client by username
    try:
        cliente = Clientes.objects.filter(nomecliente=user.username).first()
        if not cliente:
             return Response([])

        vendas = Vendas.objects.filter(clienteid=cliente).order_by('-data', '-vendaid')
        
        # Construct simple response data
        data = []
        for v in vendas:
            linhas = v.linhas.all()
            tickets = []
            for l in linhas:
                if l.bilheteid:
                    tickets.append({
                        "filme": l.bilheteid.sessaoid.filmeid.titulo,
                        "sala": l.bilheteid.sessaoid.salaid.nomesala,
                        "data": l.bilheteid.sessaoid.inicio,
                        "lugar": f"{l.bilheteid.lugarid.fila}{l.bilheteid.lugarid.numero}"
                    })
            data.append({
                "id": v.vendaid,
                "data": v.data,
                "total": v.totalvenda,
                "tickets": tickets
            })
            
        return Response(data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def produtos_api(request):
    """API endpoint to get all active products."""
    produtos = Produtos.objects.filter(ativo=True, stock__gt=0)
    serializer = ProdutosSerializer(produtos, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def comprar_produtos_api(request):
    """API to process a purchase of concession items."""
    try:
        user = request.user
        items = request.data.get('items', [])  # List of {produtoid, quantidade}

        if not items:
            return Response({"error": "No items provided"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # 1. Get/Create Client
            cliente, created = Clientes.objects.get_or_create(
                nomecliente=user.username,
                defaults={'emailcliente': user.email}
            )

            # 2. Create Venda
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

                # Update stock
                produto.stock -= qty
                produto.save()

                line_total = produto.precoproduto * qty

                # Create VendaLinha
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

            # Log purchase
            log_action(user, 'buy_concessions', 'Vendas', venda.vendaid, {"total": float(total)})

            return Response({"message": "Purchase successful", "venda_id": venda.vendaid}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

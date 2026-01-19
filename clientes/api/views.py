# /home/driblades/Documents/BD2/b2da1/clientes/api/views.py
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from clientes.core.dtos import NovoClienteDTO
from clientes.core.services import ClienteService
from clientes.core.exceptions import ClienteServiceException
from .serializers import ClienteSignupSerializer, ClienteLoginSerializer


class ClienteSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClienteSignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        dto = NovoClienteDTO(
            username=data['username'],
            password=data['password'],
            email=data.get('email', ''),
            nome_completo=data.get('nomecliente') or data['username'],
            telefone=data.get('telefonecliente'),
            nif=data.get('nif'),
            morada=data.get('moradacliente'),
            codigo_postal=data.get('codigopostalcliente'),
            localidade=data.get('localidadecliente'),
            data_nascimento=data.get('datanascimento')
        )

        service = ClienteService()
        try:
            profile = service.registrar_novo_cliente(dto)


            login(request, profile.user)

            return Response({
                "message": "Cliente criado com sucesso.",
                "user_id": profile.user.id,
                "cliente_id": profile.cliente_dados.clienteid
            }, status=status.HTTP_201_CREATED)

        except ClienteServiceException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ClienteLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClienteLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(
            request,
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if user is not None:
            login(request, user)

            service = ClienteService()
            profile = service.get_cliente_por_user(user)
            cliente_id = profile.cliente_dados.clienteid if profile else None

            return Response({
                "message": "Login realizado com sucesso",
                "username": user.username,
                "cliente_id": cliente_id
            })
        else:
            return Response({"error": "Credenciais inválidas"}, status=status.HTTP_401_UNAUTHORIZED)


class ClienteMeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = ClienteService()
        profile = service.get_cliente_por_user(request.user)

        return Response({
            "is_authenticated": True,
            "username": request.user.username,
            "cliente_id": profile.cliente_dados.clienteid if profile else None,
            "nome_display": profile.cliente_dados.nomecliente if profile else request.user.username
        })
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class ClienteSignupSerializer(serializers.Serializer):
    # Campos de Login
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    # Campos do Cliente (Dados Pessoais)
    nomecliente = serializers.CharField(required=False, max_length=100)
    telefonecliente = serializers.CharField(required=False, max_length=20)
    nif = serializers.CharField(required=False, max_length=15)
    moradacliente = serializers.CharField(required=False, max_length=150)
    codigopostalcliente = serializers.CharField(required=False, max_length=10)
    localidadecliente = serializers.CharField(required=False, max_length=50)
    datanascimento = serializers.DateField(required=False)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nome de usuário já existe.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value


class ClienteLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
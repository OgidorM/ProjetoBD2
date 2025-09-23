# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.CASCADE)
    permission = models.ForeignKey('AuthPermission', models.CASCADE)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.CASCADE)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.CASCADE)
    group = models.ForeignKey(AuthGroup, models.CASCADE)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.CASCADE)
    permission = models.ForeignKey(AuthPermission, models.CASCADE)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Bilhetes(models.Model):
    bilheteid = models.AutoField(primary_key=True)
    vendalinhaid = models.ForeignKey('Vendalinhas', models.CASCADE, db_column='vendalinhaid', blank=True, null=True)
    lugarid = models.ForeignKey('Lugares', models.CASCADE, db_column='lugarid', blank=True, null=True)
    sessaoid = models.ForeignKey('Sessoes', models.CASCADE, db_column='sessaoid', blank=True, null=True)
    precobilhete = models.DecimalField(max_digits=5, decimal_places=2)
    emicao = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'bilhetes'


class Categorias(models.Model):
    categoriaid = models.AutoField(primary_key=True)
    nomecategoria = models.CharField(max_length=80)

    class Meta:
        managed = False
        db_table = 'categorias'


class Cinemas(models.Model):
    cinemaid = models.AutoField(primary_key=True)
    nomecinema = models.CharField(max_length=80)
    emailcinema = models.CharField(max_length=254, blank=True, null=True)
    telefonecinema = models.CharField(max_length=20, blank=True, null=True)
    moradacinema = models.CharField(max_length=120, blank=True, null=True)
    codigopostalcinema = models.CharField(max_length=8, blank=True, null=True)
    localidadecinema = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = 'cinemas'


class Clientes(models.Model):
    clienteid = models.AutoField(primary_key=True)
    nomecliente = models.CharField(max_length=80, blank=True, null=True)
    emailcliente = models.CharField(max_length=254, blank=True, null=True)
    telefonecliente = models.CharField(max_length=20, blank=True, null=True)
    datanascimento = models.DateField(blank=True, null=True)
    moradacliente = models.CharField(max_length=120, blank=True, null=True)
    codigopostalcliente = models.CharField(max_length=8, blank=True, null=True)
    localidadecliente = models.CharField(max_length=60, blank=True, null=True)
    nif = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clientes'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.CASCADE)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Filmes(models.Model):
    filmeid = models.AutoField(primary_key=True)
    categoriaid = models.ForeignKey(Categorias, models.CASCADE, db_column='categoriaid', blank=True, null=True)
    cinemaid = models.ForeignKey(Cinemas, models.CASCADE, db_column='cinemaid', blank=True, null=True)
    titulo = models.CharField(max_length=120)
    datalancamento = models.DateField(blank=True, null=True)
    duracao = models.IntegerField()
    produtora = models.CharField(max_length=80, blank=True, null=True)
    fimexebicao = models.DateField(blank=True, null=True)
    idioma = models.CharField(max_length=4, blank=True, null=True)
    sinopse = models.TextField(blank=True, null=True)
    classificacaoetaria = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'filmes'


class Funcionarios(models.Model):
    funcionarioid = models.AutoField(primary_key=True)
    cinemaid = models.ForeignKey(Cinemas, models.CASCADE, db_column='cinemaid', blank=True, null=True)
    nomefuncionario = models.CharField(max_length=80)
    emailfuncionario = models.CharField(max_length=254, blank=True, null=True)
    telefonefuncionario = models.CharField(max_length=20, blank=True, null=True)
    cargo = models.CharField(max_length=20)
    admissao = models.DateField()
    salario = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'funcionarios'


class Lugares(models.Model):
    lugarid = models.AutoField(primary_key=True)
    salaid = models.ForeignKey('Salas', models.CASCADE, db_column='salaid', blank=True, null=True)
    fila = models.CharField(max_length=4)
    numero = models.IntegerField()
    tipolugar = models.CharField(max_length=20, blank=True, null=True)
    estadolugar = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lugares'


class Produtos(models.Model):
    produtoid = models.AutoField(primary_key=True)
    nomeproduto = models.CharField(max_length=80)
    precoproduto = models.DecimalField(max_digits=5, decimal_places=2)
    stock = models.IntegerField()
    ativo = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'produtos'


class Salas(models.Model):
    salaid = models.AutoField(primary_key=True)
    cinemaid = models.ForeignKey(Cinemas, models.CASCADE, db_column='cinemaid', blank=True, null=True)
    nomesala = models.CharField(max_length=80, blank=True, null=True)
    capacidade = models.IntegerField()
    tiposala = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'salas'


class Sessoes(models.Model):
    sessaoid = models.AutoField(primary_key=True)
    salaid = models.ForeignKey(Salas, models.CASCADE, db_column='salaid', blank=True, null=True)
    filmeid = models.ForeignKey(Filmes, models.CASCADE, db_column='filmeid', blank=True, null=True)
    inicio = models.DateTimeField()
    fim = models.DateTimeField()
    versao = models.CharField(max_length=8)
    estadosessao = models.CharField(max_length=20)
    precosessao = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sessoes'


class Vendalinhas(models.Model):
    vendalinhaid = models.AutoField(primary_key=True)
    vendaid = models.ForeignKey('Vendas', models.CASCADE, db_column='vendaid', blank=True, null=True)
    produtoid = models.ForeignKey(Produtos, models.PROTECT, db_column='produtoid', blank=True, null=True)
    quantidade = models.IntegerField()
    total_linha_field = models.DecimalField(db_column='total_linha_', max_digits=5, decimal_places=2, blank=True, null=True)  # Field renamed because it ended with '_'.
    precolinha = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vendalinhas'


class Vendas(models.Model):
    vendaid = models.AutoField(primary_key=True)
    clienteid = models.ForeignKey(Clientes, models.CASCADE, db_column='clienteid', blank=True, null=True)
    funcionarioid = models.ForeignKey(Funcionarios, models.CASCADE, db_column='funcionarioid', blank=True, null=True)
    data = models.DateField(blank=True, null=True)
    estadovenda = models.CharField(max_length=20, blank=True, null=True)
    totalvenda = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vendas'

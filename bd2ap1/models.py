from django.db import models

class Categorias(models.Model):
    categoriaid = models.AutoField(primary_key=True)
    nomecategoria = models.CharField(max_length=80)

    class Meta:
        managed = True
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
        managed = True
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
        managed = True
        db_table = 'clientes'


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
        managed = True
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
        managed = True
        db_table = 'funcionarios'


class Salas(models.Model):
    salaid = models.AutoField(primary_key=True)
    cinemaid = models.ForeignKey(Cinemas, models.CASCADE, db_column='cinemaid', blank=True, null=True)
    nomesala = models.CharField(max_length=80, blank=True, null=True)
    capacidade = models.IntegerField()
    tiposala = models.CharField(max_length=20)

    class Meta:
        managed = True
        db_table = 'salas'


class Lugares(models.Model):
    lugarid = models.AutoField(primary_key=True)
    salaid = models.ForeignKey(Salas, models.CASCADE, db_column='salaid', blank=True, null=True)
    fila = models.CharField(max_length=4)
    numero = models.IntegerField()
    tipolugar = models.CharField(max_length=20, blank=True, null=True)
    estadolugar = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'lugares'


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
        managed = True
        db_table = 'sessoes'


class Produtos(models.Model):
    produtoid = models.AutoField(primary_key=True)
    nomeproduto = models.CharField(max_length=80)
    precoproduto = models.DecimalField(max_digits=5, decimal_places=2)
    stock = models.IntegerField()
    ativo = models.BooleanField()

    class Meta:
        managed = True
        db_table = 'produtos'


class Vendalinhas(models.Model):
    vendalinhaid = models.AutoField(primary_key=True)
    vendaid = models.ForeignKey('Vendas', models.CASCADE, db_column='vendaid', blank=True, null=True)
    produtoid = models.ForeignKey(Produtos, models.PROTECT, db_column='produtoid', blank=True, null=True)
    quantidade = models.IntegerField()
    total_linha_field = models.DecimalField(db_column='total_linha_', max_digits=5, decimal_places=2, blank=True, null=True)
    precolinha = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'vendalinhas'


class Bilhetes(models.Model):
    bilheteid = models.AutoField(primary_key=True)
    vendalinhaid = models.ForeignKey(Vendalinhas, models.CASCADE, db_column='vendalinhaid', blank=True, null=True)
    lugarid = models.ForeignKey(Lugares, models.CASCADE, db_column='lugarid', blank=True, null=True)
    sessaoid = models.ForeignKey(Sessoes, models.CASCADE, db_column='sessaoid', blank=True, null=True)
    precobilhete = models.DecimalField(max_digits=5, decimal_places=2)
    emicao = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'bilhetes'


class Vendas(models.Model):
    vendaid = models.AutoField(primary_key=True)
    clienteid = models.ForeignKey(Clientes, models.CASCADE, db_column='clienteid', blank=True, null=True)
    funcionarioid = models.ForeignKey(Funcionarios, models.CASCADE, db_column='funcionarioid', blank=True, null=True)
    data = models.DateField(blank=True, null=True)
    estadovenda = models.CharField(max_length=20, blank=True, null=True)
    totalvenda = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'vendas'

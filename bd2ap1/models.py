# models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# === Tabelas de domínio do projeto ===

class Categorias(models.Model):
    categoriaid = models.AutoField(primary_key=True)
    nomecategoria = models.CharField(max_length=80)

    class Meta:
        db_table = 'categorias'

    def __str__(self) -> str:
        return self.nomecategoria


class Cinemas(models.Model):
    cinemaid = models.AutoField(primary_key=True)
    nomecinema = models.CharField(max_length=80)
    emailcinema = models.CharField(max_length=254, blank=True, null=True)
    telefonecinema = models.CharField(max_length=20, blank=True, null=True)
    moradacinema = models.CharField(max_length=120, blank=True, null=True)
    codigopostalcinema = models.CharField(max_length=8, blank=True, null=True)
    localidadecinema = models.CharField(max_length=60)
    ranking = models.DecimalField(
        max_digits=2, decimal_places=1, default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text='Ranking do cinema (0 a 5)'
    )

    class Meta:
        db_table = 'cinemas'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ranking__gte=0) & models.Q(ranking__lte=5),
                name='ck_cinemas_ranking_0_5',
            )
        ]

    def __str__(self) -> str:
        return self.nomecinema


class ClassificacoesEtarias(models.Model):
    classificacaoid = models.AutoField(primary_key=True)
    nomeclassificacao = models.CharField(max_length=8)

    class Meta:
        db_table = 'classificacoesetarias'

    def __str__(self) -> str:
        return self.nomeclassificacao

class Filmes(models.Model):
    filmeid = models.AutoField(primary_key=True)
    categoriaid = models.ForeignKey(
        Categorias,
        on_delete=models.CASCADE,  # SQL: NO ACTION
        db_column='categoriaid',
        related_name='filmes'
    )
    cinemaid = models.ForeignKey(
        Cinemas,
        on_delete=models.SET_NULL,
        db_column='cinemaid',
        blank=True, null=True,
        related_name='filmes'
    )
    titulo = models.CharField(max_length=120)
    datalancamento = models.DateField(blank=True, null=True)
    duracao = models.IntegerField()
    produtora = models.CharField(max_length=80, blank=True, null=True)
    fimexebicao = models.DateField(blank=True, null=True)
    idioma = models.CharField(max_length=4, blank=True, null=True)
    sinopse = models.TextField(blank=True, null=True)
    cartaz_url = models.URLField(max_length=500, blank=True, null=True)
    classificacaoetaria = models.ForeignKey(
        ClassificacoesEtarias,
        on_delete=models.CASCADE,  # SQL: NO ACTION
        db_column='classificacaoetaria',
        default=1,
        related_name='filmes'
    )
    ranking = models.DecimalField(
        max_digits=2, decimal_places=1, default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text='Ranking do filme (0 a 5)'
    )

    class Meta:
        db_table = 'filmes'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ranking__gte=0) & models.Q(ranking__lte=5),
                name='ck_filmes_ranking_0_5',
            )
        ]

    def __str__(self) -> str:
        return self.titulo

class Salas(models.Model):
    salaid = models.AutoField(primary_key=True)
    cinemaid = models.ForeignKey(
        Cinemas,
        on_delete=models.CASCADE,  # SQL: NO ACTION
        db_column='cinemaid',
        blank=True, null=True,
        related_name='salas'
    )
    nomesala = models.CharField(max_length=80, blank=True, null=True)
    capacidade = models.IntegerField(default=0, null=True)
    filas = models.IntegerField(default=0)
    colunas = models.IntegerField(default=0)
    tiposala = models.CharField(max_length=20)

    class Meta:
        db_table = 'salas'

    def __str__(self) -> str:
        return self.nomesala or f"Sala {self.salaid}"

class Sessoes(models.Model):
    sessaoid = models.AutoField(primary_key=True)
    salaid = models.ForeignKey(
        Salas,
        on_delete=models.CASCADE,  # SQL: NO ACTION
        db_column='salaid',
        blank=True, null=True,
        related_name='sessoes'
    )
    filmeid = models.ForeignKey(
        Filmes,
        on_delete=models.CASCADE,  # SQL: NO ACTION
        db_column='filmeid',
        blank=True, null=True,
        related_name='sessoes'
    )
    inicio = models.DateTimeField()
    fim = models.DateTimeField()
    versao = models.CharField(max_length=8)
    estadosessao = models.CharField(max_length=20)
    precosessao = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'sessoes'

    def __str__(self) -> str:
        return f"{self.filmeid.titulo if self.filmeid_id else 'Sessão'} @ {self.inicio:%Y-%m-%d %H:%M}"

class Lugares(models.Model):
    lugarid = models.AutoField(primary_key=True)
    salaid = models.ForeignKey(
        Salas,
        on_delete=models.CASCADE,  # SQL: NO ACTION
        db_column='salaid',
        blank=True, null=True,
        related_name='lugares'
    )
    fila = models.CharField(max_length=4)
    numero = models.IntegerField()
    tipolugar = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'lugares'
        constraints = [
            models.UniqueConstraint(
                fields=['salaid', 'fila', 'numero'], name='uq_lugares_sala_fila_numero'
            )
        ]

    def __str__(self) -> str:
        return f"Sala {self.salaid_id} - {self.fila}{self.numero}"

class LugaresSessao(models.Model):
    lugarsessaoid = models.AutoField(primary_key=True)
    lugarid = models.ForeignKey(
        Lugares,
        on_delete=models.PROTECT,
        db_column='lugarid',
        blank=True, null=True,
        related_name='lugaresta'
    )
    sessaoid = models.ForeignKey(
        Sessoes,
        on_delete=models.PROTECT,
        db_column='sessaoid',
        blank=True, null=True,
        related_name='lugaresta'
    )
    estado = models.CharField(default='Livre', max_length=20, blank=True, null=True)
    
    class Meta:
        db_table = 'lugaressessao'
        constraints = [
            models.UniqueConstraint(
                fields=['lugarsessaoid'], name='uq_lugaressessao_lugarsessaoid'
            )
        ]
    
    def __str__(self) -> str:
        return f"Lugar {self.lugarid_id} - Sessão {self.sessaoid_id}"
    

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
        db_table = 'clientes'

    def __str__(self) -> str:
        return self.nomecliente or f"Cliente {self.clienteid}"


class Funcionarios(models.Model):
    funcionarioid = models.AutoField(primary_key=True)
    cinemaid = models.ForeignKey(
        Cinemas,
        on_delete=models.CASCADE,  # SQL: NO ACTION
        db_column='cinemaid',
        blank=True, null=True,
        related_name='funcionarios'
    )
    nomefuncionario = models.CharField(max_length=80)
    emailfuncionario = models.CharField(max_length=254, blank=True, null=True)
    telefonefuncionario = models.CharField(max_length=20, blank=True, null=True)
    cargo = models.CharField(max_length=20)
    admissao = models.DateField()
    salario = models.DecimalField(max_digits=8, decimal_places=2)
    ranking = models.DecimalField(
        max_digits=2, decimal_places=1, default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text='Ranking do funcionario (0 a 5)'
    )

    class Meta:
        db_table = 'funcionarios'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ranking__gte=0) & models.Q(ranking__lte=5),
                name='ck_funcionarios_ranking_0_5',
            )
        ]

    def __str__(self) -> str:
        return self.nomefuncionario


class Produtos(models.Model):
    produtoid = models.AutoField(primary_key=True)
    nomeproduto = models.CharField(max_length=80)
    precoproduto = models.DecimalField(max_digits=5, decimal_places=2)
    stock = models.IntegerField()
    ativo = models.BooleanField()

    class Meta:
        db_table = 'produtos'

    def __str__(self) -> str:
        return self.nomeproduto


class Vendas(models.Model):
    vendaid = models.AutoField(primary_key=True)
    clienteid = models.ForeignKey(
        Clientes,
        on_delete=models.SET_NULL,  # SQL: NO ACTION
        db_column='clienteid',
        blank=True, null=True,
        related_name='vendas'
    )
    funcionarioid = models.ForeignKey(
        Funcionarios,
        on_delete=models.SET_NULL,  # SQL: NO ACTION
        db_column='funcionarioid',
        blank=True, null=True,
        related_name='vendas'
    )
    data = models.DateField(blank=True, null=True)
    estadovenda = models.CharField(max_length=20, blank=True, null=True)
    totalvenda = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'vendas'

    def __str__(self) -> str:
        return f"Venda #{self.vendaid}"


class Bilhetes(models.Model):
    bilheteid = models.AutoField(primary_key=True)
    lugarid = models.ForeignKey(
        Lugares,
        on_delete=models.CASCADE,
        db_column='lugarid',
        blank=True, null=True,
        related_name='bilhetes'
    )
    sessaoid = models.ForeignKey(
        Sessoes,
        on_delete=models.CASCADE,
        db_column='sessaoid',
        blank=True, null=True,
        related_name='bilhetes'
    )
    precobilhete = models.DecimalField(max_digits=5, decimal_places=2)
    emissao = models.DateTimeField(db_column='emissao')

    class Meta:
        db_table = 'bilhetes'

    def __str__(self) -> str:
        return f"Bilhete #{self.bilheteid}"

class VendaLinhas(models.Model):
    vendalinhaid = models.AutoField(primary_key=True)
    vendaid = models.ForeignKey(
        Vendas,
        on_delete=models.CASCADE,  # SQL: NO ACTION
        db_column='vendaid',
        blank=True, null=True,
        related_name='linhas'
    )
    produtoid = models.ForeignKey(
        Produtos,
        on_delete=models.SET_NULL,  # SQL: NO ACTION
        db_column='produtoid',
        blank=True, null=True,
        related_name='linhas_venda'
    )
    bilheteid = models.ForeignKey(
        Bilhetes,
        on_delete=models.SET_NULL,  # SQL: NO ACTION
        db_column='bilheteid',
        blank=True, null=True,
        related_name='linhas_venda'
    )
    quantidade = models.IntegerField()
    total_linha = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True, db_column='total_linha_'
    )  # no SQL a coluna termina com "_"
    precolinha = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'vendalinhas'

    def __str__(self) -> str:
        return f"Linha {self.vendalinhaid} da venda {self.vendaid_id}"


class Avaliacoes(models.Model):
    avaliacaoid = models.AutoField(primary_key=True)
    venda = models.OneToOneField(  # SQL: VENDAID UNIQUE NOT NULL
        Vendas,
        on_delete=models.CASCADE,  # SQL: ON DELETE CASCADE
        db_column='vendaid',
        related_name='avaliacao'
    )
    tituloavaliacao = models.CharField(max_length=80)
    avaliacaocinema = models.IntegerField(blank=True, null=True)
    avaliacaofilme = models.IntegerField(blank=True, null=True)
    avaliacaofuncionario = models.IntegerField(blank=True, null=True)
    comentario = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        db_table = 'avaliacoes'

    def __str__(self) -> str:
        return f"Avaliação venda {self.venda_id}"
from django.core.management.base import BaseCommand
from bd2ap1.models import Categorias, Cinemas, ClassificacoesEtarias, Filmes, Salas, Sessoes, Lugares, Clientes, Funcionarios, Produtos, Vendas
from faker import Faker
import random
from django.utils import timezone

class Command(BaseCommand):
    help = 'Fill bd2ap1 tables with random data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Fill Categorias
        for _ in range(10):
            Categorias.objects.create(
                nomecategoria=fake.word().capitalize()
            )
        self.stdout.write(self.style.SUCCESS('Categorias table filled.'))

        # Fill ClassificacoesEtarias
        for age in ["L", "10", "12", "14", "16", "18"]:
            ClassificacoesEtarias.objects.create(
                nomeclassificacao=age
            )
        self.stdout.write(self.style.SUCCESS('ClassificacoesEtarias table filled.'))

        # Fill Cinemas
        for _ in range(10):
            Cinemas.objects.create(
                nomecinema=fake.company(),
                emailcinema=fake.email()[:254],
                telefonecinema=fake.phone_number()[:20],
                moradacinema=fake.street_address(),
                codigopostalcinema=fake.postcode()[:8],
                localidadecinema=fake.city(),
                ranking=round(random.uniform(0, 5), 1)
            )
        self.stdout.write(self.style.SUCCESS('Cinemas table filled.'))

        # Fill Filmes
        categorias = list(Categorias.objects.all())
        cinemas = list(Cinemas.objects.all())
        classificacoes = list(ClassificacoesEtarias.objects.all())
        filmes = []
        for _ in range(20):
            filme = Filmes.objects.create(
                categoriaid=random.choice(categorias),
                cinemaid=random.choice(cinemas),
                titulo=fake.sentence(nb_words=3)[:120],
                datalancamento=fake.date_between(start_date='-5y', end_date='today'),
                duracao=random.randint(60, 180),
                produtora=fake.company()[:80],
                fimexebicao=fake.date_between(start_date='today', end_date='+1y'),
                idioma=random.choice(['PT', 'EN', 'ES', 'FR']),
                sinopse=fake.text(max_nb_chars=200),
                classificacaoetaria=random.choice(classificacoes),
                ranking=round(random.uniform(0, 5), 1)
            )
            filmes.append(filme)
        self.stdout.write(self.style.SUCCESS('Filmes table filled.'))

        # Fill Salas
        salas = []
        for _ in range(10):
            sala = Salas.objects.create(
                cinemaid=random.choice(cinemas),
                nomesala=fake.word().capitalize()[:80],
                capacidade=random.randint(50, 200),
                tiposala=random.choice(['Normal', 'IMAX', 'VIP', '3D'])[:20]
            )
            salas.append(sala)
        self.stdout.write(self.style.SUCCESS('Salas table filled.'))

        # Fill Sessoes
        sessoes = []
        for _ in range(30):
            sala = random.choice(salas)
            filme = random.choice(filmes)
            inicio_naive = fake.date_time_between(start_date='-1y', end_date='now')
            fim_naive = fake.date_time_between(start_date=inicio_naive, end_date='+3h')
            inicio = timezone.make_aware(inicio_naive)
            fim = timezone.make_aware(fim_naive)
            sessao = Sessoes.objects.create(
                salaid=sala,
                filmeid=filme,
                inicio=inicio,
                fim=fim,
                versao=random.choice(['Legendado', 'Dublado'])[:8],
                estadosessao=random.choice(['Ativa', 'Cancelada', 'Finalizada'])[:20],
                precosessao=round(random.uniform(5, 20), 2)
            )
            sessoes.append(sessao)
        self.stdout.write(self.style.SUCCESS('Sessoes table filled.'))

        # Fill Lugares
        for sala in salas:
            for fila in ['A', 'B', 'C', 'D', 'E']:
                for numero in range(1, 11):
                    Lugares.objects.create(
                        salaid=sala,
                        fila=fila,
                        numero=numero,
                        tipolugar=random.choice(['Normal', 'VIP', 'Acessível'])[:20],
                        estadolugar=random.choice(['Livre', 'Reservado', 'Ocupado'])[:20]
                    )
        self.stdout.write(self.style.SUCCESS('Lugares table filled.'))

        # Fill Clientes
        clientes = []
        for _ in range(20):
            cliente = Clientes.objects.create(
                nomecliente=fake.name()[:80],
                emailcliente=fake.email()[:254],
                telefonecliente=fake.phone_number()[:20],
                datanascimento=fake.date_of_birth(minimum_age=18, maximum_age=80),
                moradacliente=fake.street_address()[:120],
                codigopostalcliente=fake.postcode()[:8],
                localidadecliente=fake.city()[:60],
                nif=fake.bothify(text='###########')[:15]
            )
            clientes.append(cliente)
        self.stdout.write(self.style.SUCCESS('Clientes table filled.'))

        # Fill Funcionarios
        for _ in range(10):
            Funcionarios.objects.create(
                cinemaid=random.choice(cinemas),
                nomefuncionario=fake.name()[:80],
                emailfuncionario=fake.email()[:254],
                telefonefuncionario=fake.phone_number()[:20],
                cargo=random.choice(['Gerente', 'Atendente', 'Limpeza', 'Técnico'])[:20],
                admissao=fake.date_between(start_date='-10y', end_date='today'),
                salario=round(random.uniform(800, 5000), 2),
                ranking=round(random.uniform(0, 5), 1)
            )
        self.stdout.write(self.style.SUCCESS('Funcionarios table filled.'))

        # Fill Produtos
        for _ in range(15):
            Produtos.objects.create(
                nomeproduto=fake.word().capitalize()[:80],
                precoproduto=round(random.uniform(1, 50), 2),
                stock=random.randint(0, 200),
                ativo=random.choice([True, False])
            )
        self.stdout.write(self.style.SUCCESS('Produtos table filled.'))

        # Fill Vendas
        for _ in range(30):
            Vendas.objects.create(
                clienteid=random.choice(clientes)
            )
        self.stdout.write(self.style.SUCCESS('Vendas table filled.'))

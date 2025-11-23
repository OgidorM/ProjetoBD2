from django.core.management.base import BaseCommand
from bd2ap1.models import (
    Categorias, Cinemas, ClassificacoesEtarias, Filmes, Salas,
    Sessoes, Lugares, Clientes, Funcionarios, Produtos,
    Vendas, VendaLinhas, Avaliacoes, Bilhetes
)
from faker import Faker
import random
from django.utils import timezone
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Fill bd2ap1 tables with random data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        self.stdout.write(self.style.WARNING('Cleaning old data...'))
        # Apagar por ordem de dependência (filhos primeiro)
        Avaliacoes.objects.all().delete()
        VendaLinhas.objects.all().delete()
        Bilhetes.objects.all().delete()
        Vendas.objects.all().delete()
        Sessoes.objects.all().delete()
        Lugares.objects.all().delete()
        Salas.objects.all().delete()
        Filmes.objects.all().delete()
        Funcionarios.objects.all().delete()
        Produtos.objects.all().delete()
        Clientes.objects.all().delete()
        Cinemas.objects.all().delete()
        Categorias.objects.all().delete()
        ClassificacoesEtarias.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Database cleaned. Starting seeding...'))

        # Fill Categorias
        categorias = []
        for _ in range(10):
            c = Categorias.objects.create(nomecategoria=fake.word().capitalize())
            categorias.append(c)
        self.stdout.write(self.style.SUCCESS('Categorias table filled.'))

        # Fill ClassificacoesEtarias
        classificacoes = []
        for age in ["L", "10", "12", "14", "16", "18"]:
            c = ClassificacoesEtarias.objects.create(nomeclassificacao=age)
            classificacoes.append(c)
        self.stdout.write(self.style.SUCCESS('ClassificacoesEtarias table filled.'))

        # Fill Cinemas
        cinemas = []
        for _ in range(5):  # Reduzi para 5 para não poluir muito
            c = Cinemas.objects.create(
                nomecinema=fake.company(),
                emailcinema=fake.email()[:254],
                telefonecinema=fake.phone_number()[:20],
                moradacinema=fake.street_address(),
                codigopostalcinema=fake.postcode()[:8],
                localidadecinema=fake.city(),
                ranking=round(random.uniform(0, 5), 1)
            )
            cinemas.append(c)
        self.stdout.write(self.style.SUCCESS('Cinemas table filled.'))

        # Fill Filmes
        filmes = []
        for _ in range(20):
            filme = Filmes.objects.create(
                categoriaid=random.choice(categorias),
                cinemaid=random.choice(cinemas),
                titulo=fake.catch_phrase()[:120],  # Catch phrase parece mais titulo de filme
                datalancamento=fake.date_between(start_date='-2y', end_date='today'),
                duracao=random.randint(90, 180),
                produtora=fake.company()[:80],
                fimexebicao=fake.date_between(start_date='today', end_date='+60d'),
                idioma=random.choice(['PT', 'EN', 'ES', 'FR']),
                sinopse=fake.text(max_nb_chars=200),
                classificacaoetaria=random.choice(classificacoes),
                ranking=round(random.uniform(0, 5), 1)
            )
            filmes.append(filme)
        self.stdout.write(self.style.SUCCESS('Filmes table filled.'))

        # Fill Salas
        salas = []
        for cinema in cinemas:
            for i in range(1, 4):  # 3 salas por cinema
                sala = Salas.objects.create(
                    cinemaid=cinema,
                    nomesala=f"Sala {i}",
                    capacidade=random.randint(50, 200),
                    tiposala=random.choice(['Normal', 'IMAX', 'VIP', '3D'])[:20]
                )
                salas.append(sala)
        self.stdout.write(self.style.SUCCESS('Salas table filled.'))

        # Fill Lugares (Para cada sala)
        todos_lugares = []  # Guardar para usar nos bilhetes depois
        for sala in salas:
            for fila in ['A', 'B', 'C', 'D', 'E']:
                for numero in range(1, 11):  # 10 lugares por fila
                    lugar = Lugares.objects.create(
                        salaid=sala,
                        fila=fila,
                        numero=numero,
                        tipolugar='Normal',
                        estadolugar='Livre'
                    )
                    todos_lugares.append(lugar)
        self.stdout.write(self.style.SUCCESS('Lugares table filled.'))

        # Fill Sessoes
        sessoes = []
        for _ in range(50):
            sala = random.choice(salas)
            filme = Filmes.objects.filter(cinemaid=sala.cinemaid).first()  # Filme tem de ser do mesmo cinema
            if not filme: continue

            # Gerar hora de inicio
            hora_inicio = random.randint(10, 22)
            minuto_inicio = random.choice([0, 15, 30, 45])

            # Objetos TIME e não DATETIME
            inicio = datetime.strptime(f"{hora_inicio}:{minuto_inicio}", "%H:%M").time()

            # Fim é inicio + duração do filme (aprox)
            minutos_total = hora_inicio * 60 + minuto_inicio + filme.duracao + 20  # +20min trailers
            hora_fim = (minutos_total // 60) % 24
            minuto_fim = minutes_total = minutos_total % 60
            fim = datetime.strptime(f"{hora_fim}:{minuto_fim}", "%H:%M").time()

            sessao = Sessoes.objects.create(
                salaid=sala,
                filmeid=filme,
                inicio=inicio,
                fim=fim,
                versao=random.choice(['Legendado', 'Dobrado'])[:8],
                estadosessao=random.choice(['Ativa', 'Finalizada']),
                precosessao=round(random.uniform(5, 12), 2)
            )
            sessoes.append(sessao)
        self.stdout.write(self.style.SUCCESS('Sessoes table filled.'))

        # Fill Clientes
        clientes = []
        for _ in range(20):
            cliente = Clientes.objects.create(
                nomecliente=fake.name()[:80],
                emailcliente=fake.email()[:254],
                telefonecliente=fake.phone_number()[:20],
                datanascimento=fake.date_of_birth(minimum_age=18, maximum_age=80),
                moradacliente=fake.address()[:120],
                codigopostalcliente=fake.postcode()[:8],
                localidadecliente=fake.city()[:60],
                nif=fake.random_number(digits=9)
            )
            clientes.append(cliente)
        self.stdout.write(self.style.SUCCESS('Clientes table filled.'))

        # Fill Funcionarios
        funcionarios = []
        for _ in range(10):
            func = Funcionarios.objects.create(
                cinemaid=random.choice(cinemas),
                nomefuncionario=fake.name()[:80],
                emailfuncionario=fake.email()[:254],
                telefonefuncionario=fake.phone_number()[:20],
                cargo=random.choice(['Gerente', 'Atendente', 'Limpeza', 'Técnico'])[:20],
                admissao=fake.date_between(start_date='-10y', end_date='today'),
                salario=round(random.uniform(800, 5000), 2),
                ranking=round(random.uniform(0, 5), 1)
            )
            funcionarios.append(func)
        self.stdout.write(self.style.SUCCESS('Funcionarios table filled.'))

        # Fill Produtos
        produtos = []
        for _ in range(10):
            prod = Produtos.objects.create(
                nomeproduto=fake.word().capitalize() + " " + random.choice(['Grande', 'Médio', 'Pequeno']),
                precoproduto=round(random.uniform(2, 15), 2),
                stock=random.randint(0, 200),
                ativo=True
            )
            produtos.append(prod)
        self.stdout.write(self.style.SUCCESS('Produtos table filled.'))

        # Fill Vendas, Bilhetes e VendaLinhas
        for _ in range(40):
            cli = random.choice(clientes)
            # Escolhe um funcionário qualquer (idealmente seria do cinema onde foi a sessão, mas simplificamos)
            func = random.choice(funcionarios)

            venda = Vendas.objects.create(
                clienteid=cli,
                funcionarioid=func,
                data=fake.date_this_year(),
                estadovenda='Concluída',
                totalvenda=0  # Vamos calcular abaixo
            )

            total_da_venda = 0

            # 1. Adicionar Bilhetes à venda (Opcional, 70% chance)
            if random.random() > 0.3 and sessoes:
                sessao = random.choice(sessoes)
                # Tenta arranjar um lugar dessa sala
                lugar = Lugares.objects.filter(salaid=sessao.salaid).order_by('?').first()

                if lugar:
                    # Cria o bilhete
                    bilhete = Bilhetes.objects.create(
                        lugarid=lugar,
                        sessaoid=sessao,
                        precobilhete=sessao.precosessao,
                        emissao=timezone.now()
                    )

                    # Cria a linha da venda para o bilhete
                    VendaLinhas.objects.create(
                        vendaid=venda,
                        bilheteid=bilhete,
                        produtoid=None,  # Linha de bilhete não tem produto
                        quantidade=1,
                        precolinha=sessao.precosessao,
                        total_linha=sessao.precosessao
                    )
                    total_da_venda += float(sessao.precosessao)

            # 2. Adicionar Produtos à venda (Opcional, 70% chance)
            if random.random() > 0.3 and produtos:
                num_prods = random.randint(1, 3)
                for _ in range(num_prods):
                    prod = random.choice(produtos)
                    qtd = random.randint(1, 3)
                    total_linha = float(prod.precoproduto) * qtd

                    VendaLinhas.objects.create(
                        vendaid=venda,
                        bilheteid=None,  # Linha de produto não tem bilhete
                        produtoid=prod,
                        quantidade=qtd,
                        precolinha=prod.precoproduto,
                        total_linha=total_linha
                    )
                    total_da_venda += total_linha

            # Atualizar total da venda
            venda.totalvenda = total_da_venda
            venda.save()

            # Criar avaliação se houve venda (30% chance)
            if total_da_venda > 0 and random.random() > 0.7:
                Avaliacoes.objects.create(
                    venda=venda,
                    tituloavaliacao=fake.sentence(nb_words=3)[:80],
                    avaliacaocinema=random.randint(3, 5),
                    avaliacaofilme=random.randint(3, 5),
                    avaliacaofuncionario=random.randint(3, 5),
                    comentario=fake.text(max_nb_chars=100)
                )

        self.stdout.write(self.style.SUCCESS('Vendas, Bilhetes e Linhas filled.'))
        self.stdout.write(self.style.SUCCESS('--- DONE ---'))
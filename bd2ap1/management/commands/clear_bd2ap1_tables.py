from django.core.management.base import BaseCommand
from django.db import connection
from bd2ap1.models import Sessoes, Lugares, Salas, Filmes, Categorias, Cinemas, ClassificacoesEtarias, Clientes, Funcionarios, Produtos, Vendas, VendaLinhas, Avaliacoes

class Command(BaseCommand):
    help = 'Clear all bd2ap1 tables in correct order to avoid FK constraint errors.'

    def handle(self, *args, **kwargs):
        # Delete child tables first
        VendaLinhas.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('VendaLinhas table cleared.'))
        Avaliacoes.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Avaliacoes table cleared.'))
        Sessoes.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Sessoes table cleared.'))
        Lugares.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Lugares table cleared.'))
        Salas.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Salas table cleared.'))
        Filmes.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Filmes table cleared.'))
        Categorias.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Categorias table cleared.'))
        ClassificacoesEtarias.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('ClassificacoesEtarias table cleared.'))
        Vendas.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Vendas table cleared.'))
        Produtos.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Produtos table cleared.'))
        Clientes.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Clientes table cleared.'))
        Funcionarios.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Funcionarios table cleared.'))
        Cinemas.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Cinemas table cleared.'))

        # Reset primary key sequences for all tables
        table_sequence_map = {
            'categorias': 'categoriaid',
            'cinemas': 'cinemaid',
            'classificacoesetarias': 'classificacaoid',
            'filmes': 'filmeid',
            'salas': 'salaid',
            'sessoes': 'sessaoid',
            'lugares': 'lugarid',
            'clientes': 'clienteid',
            'funcionarios': 'funcionarioid',
            'produtos': 'produtoid',
            'vendas': 'vendaid',
            'vendalinhas': 'vendalinhaid',
            'avaliacoes': 'avaliacaoid',
        }
        with connection.cursor() as cursor:
            for table, pk in table_sequence_map.items():
                cursor.execute(f"ALTER SEQUENCE {table}_{pk}_seq RESTART WITH 1;")
        self.stdout.write(self.style.SUCCESS('Primary key sequences reset for all tables.'))

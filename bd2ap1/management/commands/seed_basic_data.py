from django.core.management.base import BaseCommand
from bd2ap1.models import Categorias, ClassificacoesEtarias, Cinemas, Produtos

class Command(BaseCommand):
    help = 'Adiciona dados básicos sem apagar nada'

    def handle(self, *args, **kwargs):
        # 1. Categorias
        cats = ['Ação', 'Comédia', 'Drama', 'Terror', 'Ficção Científica']
        for name in cats:
            Categorias.objects.get_or_create(nomecategoria=name)
        
        # 2. Classificações
        ages = ["L", "10", "12", "14", "16", "18"]
        for age in ages:
            ClassificacoesEtarias.objects.get_or_create(nomeclassificacao=age)

        # 3. Cinema Padrão
        Cinemas.objects.get_or_create(
            nomecinema="CineTugal Central",
            defaults={
                "localidadecinema": "Lisboa",
                "emailcinema": "central@cinetugal.pt",
                "ranking": 5.0
            }
        )

        # 4. Produtos Iniciais
        prods = [
            ("Pipocas Grandes", 5.50, 100),
            ("Pipocas Médias", 4.00, 150),
            ("Refrigerante 500ml", 3.00, 200),
            ("Nacho Pack", 6.50, 80),
        ]
        for nome, preco, stock in prods:
            Produtos.objects.get_or_create(
                nomeproduto=nome,
                defaults={"precoproduto": preco, "stock": stock, "ativo": True}
            )

        self.stdout.write(self.style.SUCCESS('Dados básicos inseridos com sucesso (sem apagar nada)!'))

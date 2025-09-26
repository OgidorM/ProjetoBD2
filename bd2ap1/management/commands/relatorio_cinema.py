# bd2ap1/management/commands/relatorio_cinema.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from bd2ap1.procedimentos import CinemaProcedures, CinemaViews
from bd2ap1.models import Cinemas
import json
from datetime import date, datetime


class Command(BaseCommand):
    help = 'Gera relatórios do sistema de cinema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo',
            type=str,
            default='mensal',
            choices=['mensal', 'receita', 'ocupacao', 'filmes', 'sessoes'],
            help='Tipo de relatório a gerar'
        )
        parser.add_argument(
            '--mes',
            type=int,
            default=timezone.now().month,
            help='Mês para relatório mensal (1-12)'
        )
        parser.add_argument(
            '--ano',
            type=int,
            default=timezone.now().year,
            help='Ano para relatório mensal'
        )
        parser.add_argument(
            '--cinema',
            type=int,
            help='ID do cinema (opcional)'
        )
        parser.add_argument(
            '--data-inicio',
            type=str,
            help='Data de início para relatório de receita (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--data-fim',
            type=str,
            help='Data de fim para relatório de receita (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--formato',
            type=str,
            default='tabela',
            choices=['tabela', 'json'],
            help='Formato de saída'
        )

    def handle(self, *args, **options):
        tipo = options['tipo']
        formato = options['formato']

        try:
            if tipo == 'mensal':
                dados = self.relatorio_mensal(options)
            elif tipo == 'receita':
                dados = self.relatorio_receita(options)
            elif tipo == 'ocupacao':
                dados = self.relatorio_ocupacao()
            elif tipo == 'filmes':
                dados = self.relatorio_filmes()
            elif tipo == 'sessoes':
                dados = self.relatorio_sessoes(options)
            else:
                self.stdout.write(
                    self.style.ERROR(f'Tipo de relatório não reconhecido: {tipo}')
                )
                return

            if formato == 'json':
                self.output_json(dados)
            else:
                self.output_tabela(dados, tipo)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao gerar relatório: {str(e)}')
            )

    def relatorio_mensal(self, options):
        """Gera relatório mensal."""
        mes = options['mes']
        ano = options['ano']
        cinema_id = options['cinema']
        
        self.stdout.write(f'Gerando relatório mensal para {mes}/{ano}...')
        return CinemaProcedures.relatorio_mensal(mes, ano, cinema_id)

    def relatorio_receita(self, options):
        """Gera relatório de receita por período."""
        data_inicio_str = options['data_inicio']
        data_fim_str = options['data_fim']
        cinema_id = options['cinema']

        if not data_inicio_str or not data_fim_str:
            # Default para o mês atual
            hoje = date.today()
            data_inicio = date(hoje.year, hoje.month, 1)
            if hoje.month == 12:
                data_fim = date(hoje.year + 1, 1, 1)
            else:
                data_fim = date(hoje.year, hoje.month + 1, 1)
        else:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()

        self.stdout.write(f'Gerando relatório de receita de {data_inicio} a {data_fim}...')
        return CinemaProcedures.calcular_receita_periodo(data_inicio, data_fim, cinema_id)

    def relatorio_ocupacao(self):
        """Gera relatório de ocupação de salas."""
        self.stdout.write('Gerando relatório de ocupação de salas...')
        return CinemaViews.ocupacao_salas()

    def relatorio_filmes(self):
        """Gera relatório de popularidade de filmes."""
        self.stdout.write('Gerando relatório de popularidade de filmes...')
        return CinemaViews.filmes_popularidade()

    def relatorio_sessoes(self, options):
        """Gera relatório de sessões."""
        cinema_id = options['cinema']
        filtros = {}
        
        if cinema_id:
            try:
                cinema = Cinemas.objects.get(cinemaid=cinema_id)
                filtros['cinema'] = cinema.nomecinema
            except Cinemas.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Cinema com ID {cinema_id} não encontrado')
                )

        self.stdout.write('Gerando relatório de sessões...')
        return CinemaViews.sessoes_completas(filtros)

    def output_json(self, dados):
        """Saída em formato JSON."""
        # Converter objetos datetime para string para serialização JSON
        dados_serializaveis = []
        for item in dados:
            item_convertido = {}
            for chave, valor in item.items():
                if isinstance(valor, (date, datetime)):
                    item_convertido[chave] = valor.isoformat()
                else:
                    item_convertido[chave] = valor
            dados_serializaveis.append(item_convertido)
        
        self.stdout.write(json.dumps(dados_serializaveis, indent=2, ensure_ascii=False))

    def output_tabela(self, dados, tipo):
        """Saída em formato de tabela."""
        if not dados:
            self.stdout.write(self.style.WARNING('Nenhum dado encontrado.'))
            return

        # Cabeçalhos baseados no tipo de relatório
        if tipo == 'mensal':
            self.stdout.write(
                self.style.SUCCESS('\n=== RELATÓRIO MENSAL ===')
            )
            for item in dados:
                self.stdout.write(f"Cinema: {item.get('cinema', 'N/A')}")
                self.stdout.write(f"  Sessões: {item.get('total_sessoes', 0)}")
                self.stdout.write(f"  Bilhetes: {item.get('total_bilhetes', 0)}")
                self.stdout.write(f"  Receita: €{item.get('receita_total', 0):.2f}")
                self.stdout.write(f"  Filme Popular: {item.get('filme_mais_popular', 'N/A')}")
                self.stdout.write(f"  Taxa Ocupação: {item.get('taxa_ocupacao_media', 0):.2f}%")
                self.stdout.write('-' * 50)

        elif tipo == 'receita':
            self.stdout.write(
                self.style.SUCCESS('\n=== RELATÓRIO DE RECEITA ===')
            )
            total_geral = 0
            for item in dados:
                receita = float(item.get('receita_total', 0))
                total_geral += receita
                self.stdout.write(f"Cinema: {item.get('cinema', 'N/A')}")
                self.stdout.write(f"  Vendas: {item.get('total_vendas', 0)}")
                self.stdout.write(f"  Receita Bilhetes: €{item.get('receita_bilhetes', 0):.2f}")
                self.stdout.write(f"  Receita Produtos: €{item.get('receita_produtos', 0):.2f}")
                self.stdout.write(f"  Receita Total: €{receita:.2f}")
                self.stdout.write('-' * 50)
            self.stdout.write(f"TOTAL GERAL: €{total_geral:.2f}")

        elif tipo == 'ocupacao':
            self.stdout.write(
                self.style.SUCCESS('\n=== RELATÓRIO DE OCUPAÇÃO ===')
            )
            for item in dados:
                self.stdout.write(f"Sala: {item.get('nomesala', 'N/A')} - {item.get('nomecinema', 'N/A')}")
                self.stdout.write(f"  Capacidade: {item.get('capacidade', 0)}")
                self.stdout.write(f"  Tipo: {item.get('tiposala', 'N/A')}")
                self.stdout.write(f"  Sessões: {item.get('total_sessoes', 0)}")
                self.stdout.write(f"  Bilhetes Vendidos: {item.get('total_bilhetes_vendidos', 0)}")
                self.stdout.write(f"  Taxa Ocupação: {item.get('taxa_ocupacao_media', 0):.2f}%")
                self.stdout.write('-' * 50)

        elif tipo == 'filmes':
            self.stdout.write(
                self.style.SUCCESS('\n=== RANKING DE FILMES ===')
            )
            for i, item in enumerate(dados[:20], 1):  # Top 20
                self.stdout.write(f"{i}. {item.get('titulo', 'N/A')}")
                self.stdout.write(f"   Cinema: {item.get('nomecinema', 'N/A')}")
                self.stdout.write(f"   Categoria: {item.get('nomecategoria', 'N/A')}")
                self.stdout.write(f"   Bilhetes Vendidos: {item.get('total_bilhetes_vendidos', 0)}")
                self.stdout.write(f"   Receita: €{item.get('receita_total', 0):.2f}")
                self.stdout.write(f"   Avaliação Média: {item.get('avaliacao_media', 'N/A')}")
                self.stdout.write('-' * 50)

        elif tipo == 'sessoes':
            self.stdout.write(
                self.style.SUCCESS('\n=== RELATÓRIO DE SESSÕES ===')
            )
            for item in dados:
                inicio = item.get('inicio')
                if isinstance(inicio, datetime):
                    inicio_str = inicio.strftime('%d/%m/%Y %H:%M')
                else:
                    inicio_str = str(inicio) if inicio else 'N/A'
                
                self.stdout.write(f"Sessão: {item.get('filme', 'N/A')}")
                self.stdout.write(f"  Cinema: {item.get('nomecinema', 'N/A')}")
                self.stdout.write(f"  Sala: {item.get('nomesala', 'N/A')}")
                self.stdout.write(f"  Início: {inicio_str}")
                self.stdout.write(f"  Estado: {item.get('estadosessao', 'N/A')}")
                self.stdout.write(f"  Preço: €{item.get('precosessao', 0):.2f}")
                self.stdout.write(f"  Ocupação: {item.get('bilhetes_vendidos', 0)}/{item.get('capacidade', 0)} ({item.get('taxa_ocupacao', 0):.1f}%)")
                self.stdout.write('-' * 50)
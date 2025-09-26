# bd2ap1/management/commands/manutencao_cinema.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from bd2ap1.procedimentos import CinemaProcedures
from bd2ap1.models import Sessoes, Vendas, Bilhetes
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Comandos de manutenção do sistema de cinema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--acao',
            type=str,
            required=True,
            choices=['limpar_sessoes', 'estatisticas', 'verificar_integridade'],
            help='Ação de manutenção a executar'
        )
        parser.add_argument(
            '--dias',
            type=int,
            default=90,
            help='Número de dias para limpeza de sessões antigas'
        )
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirma a execução da ação (obrigatório para ações destrutivas)'
        )

    def handle(self, *args, **options):
        acao = options['acao']

        try:
            if acao == 'limpar_sessoes':
                self.limpar_sessoes_antigas(options)
            elif acao == 'estatisticas':
                self.mostrar_estatisticas()
            elif acao == 'verificar_integridade':
                self.verificar_integridade()
            else:
                self.stdout.write(
                    self.style.ERROR(f'Ação não reconhecida: {acao}')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro durante manutenção: {str(e)}')
            )

    def limpar_sessoes_antigas(self, options):
        """Remove sessões antigas finalizadas."""
        dias = options['dias']
        confirmar = options['confirmar']

        # Contar sessões que serão removidas
        data_limite = timezone.now().date() - timedelta(days=dias)
        sessoes_antigas = Sessoes.objects.filter(
            fim__date__lt=data_limite,
            estadosessao='Finalizada'
        ).count()

        self.stdout.write(f'Encontradas {sessoes_antigas} sessões antigas para remoção (mais de {dias} dias).')

        if sessoes_antigas == 0:
            self.stdout.write(self.style.SUCCESS('Nenhuma sessão antiga encontrada.'))
            return

        if not confirmar:
            self.stdout.write(
                self.style.WARNING(
                    'Esta operação removerá dados permanentemente. '
                    'Use --confirmar para executar.'
                )
            )
            return

        # Executar limpeza usando a procedure
        removidas = CinemaProcedures.limpar_sessoes_antigas(dias)
        
        self.stdout.write(
            self.style.SUCCESS(f'{removidas} sessões antigas foram removidas com sucesso.')
        )

    def mostrar_estatisticas(self):
        """Mostra estatísticas gerais do sistema."""
        self.stdout.write(self.style.SUCCESS('\n=== ESTATÍSTICAS DO SISTEMA ==='))

        # Estatísticas básicas
        total_sessoes = Sessoes.objects.count()
        total_vendas = Vendas.objects.count()
        total_bilhetes = Bilhetes.objects.count()

        self.stdout.write(f'Total de Sessões: {total_sessoes}')
        self.stdout.write(f'Total de Vendas: {total_vendas}')
        self.stdout.write(f'Total de Bilhetes: {total_bilhetes}')

        # Sessões por estado
        self.stdout.write('\n--- Sessões por Estado ---')
        estados = Sessoes.objects.values('estadosessao').distinct()
        for estado in estados:
            if estado['estadosessao']:
                count = Sessoes.objects.filter(estadosessao=estado['estadosessao']).count()
                self.stdout.write(f'{estado["estadosessao"]}: {count}')

        # Vendas por estado
        self.stdout.write('\n--- Vendas por Estado ---')
        estados_venda = Vendas.objects.values('estadovenda').distinct()
        for estado in estados_venda:
            if estado['estadovenda']:
                count = Vendas.objects.filter(estadovenda=estado['estadovenda']).count()
                self.stdout.write(f'{estado["estadovenda"]}: {count}')

        # Receita total aproximada
        from django.db.models import Sum
        receita_total = Bilhetes.objects.aggregate(
            total=Sum('precobilhete')
        )['total'] or 0
        self.stdout.write(f'\nReceita Total (Bilhetes): €{receita_total:.2f}')

        # Sessões nas próximas 24 horas
        amanha = timezone.now() + timedelta(days=1)
        sessoes_proximas = Sessoes.objects.filter(
            inicio__gte=timezone.now(),
            inicio__lte=amanha
        ).count()
        self.stdout.write(f'Sessões nas próximas 24h: {sessoes_proximas}')

    def verificar_integridade(self):
        """Verifica a integridade dos dados."""
        self.stdout.write(self.style.SUCCESS('\n=== VERIFICAÇÃO DE INTEGRIDADE ==='))

        problemas = []
        avisos = []

        # Verificar bilhetes sem venda associada
        from bd2ap1.models import VendaLinhas
        bilhetes_sem_venda = Bilhetes.objects.exclude(
            bilheteid__in=VendaLinhas.objects.values('bilheteid')
        ).count()
        
        if bilhetes_sem_venda > 0:
            problemas.append(f'{bilhetes_sem_venda} bilhetes sem linha de venda associada')

        # Verificar sessões sem fim
        sessoes_sem_fim = Sessoes.objects.filter(fim__isnull=True).count()
        if sessoes_sem_fim > 0:
            problemas.append(f'{sessoes_sem_fim} sessões sem data/hora de fim')

        # Verificar sessões com início posterior ao fim
        from django.db.models import F
        sessoes_inconsistentes = Sessoes.objects.filter(inicio__gt=F('fim')).count()
        if sessoes_inconsistentes > 0:
            problemas.append(f'{sessoes_inconsistentes} sessões com início posterior ao fim')

        # Verificar vendas sem total
        vendas_sem_total = Vendas.objects.filter(totalvenda__isnull=True).count()
        if vendas_sem_total > 0:
            avisos.append(f'{vendas_sem_total} vendas sem valor total')

        # Verificar produtos com stock negativo
        from bd2ap1.models import Produtos
        produtos_stock_negativo = Produtos.objects.filter(stock__lt=0).count()
        if produtos_stock_negativo > 0:
            avisos.append(f'{produtos_stock_negativo} produtos com stock negativo')

        # Sessões no passado ainda não finalizadas
        sessoes_passado = Sessoes.objects.filter(
            fim__lt=timezone.now(),
            estadosessao__in=['Programada', 'Em Curso']
        ).count()
        if sessoes_passado > 0:
            avisos.append(f'{sessoes_passado} sessões no passado não marcadas como finalizadas')

        # Relatório final
        if problemas:
            self.stdout.write(self.style.ERROR('\n--- PROBLEMAS ENCONTRADOS ---'))
            for problema in problemas:
                self.stdout.write(self.style.ERROR(f'• {problema}'))

        if avisos:
            self.stdout.write(self.style.WARNING('\n--- AVISOS ---'))
            for aviso in avisos:
                self.stdout.write(self.style.WARNING(f'• {aviso}'))

        if not problemas and not avisos:
            self.stdout.write(self.style.SUCCESS('✓ Nenhum problema de integridade encontrado.'))
        else:
            total_issues = len(problemas) + len(avisos)
            self.stdout.write(f'\nTotal de questões encontradas: {total_issues}')

        self.stdout.write('\n--- RECOMENDAÇÕES ---')
        self.stdout.write('• Execute verificações regulares de integridade')
        self.stdout.write('• Considere agendar limpeza automática de sessões antigas')
        self.stdout.write('• Monitore vendas sem totais calculados')
        self.stdout.write('• Atualize estados de sessões expiradas')
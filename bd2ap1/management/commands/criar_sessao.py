# bd2ap1/management/commands/criar_sessao.py
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from bd2ap1.procedimentos import CinemaProcedures
from bd2ap1.models import Salas, Filmes
from datetime import datetime


class Command(BaseCommand):
    help = 'Cria uma nova sessão usando a procedure SQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sala',
            type=int,
            required=True,
            help='ID da sala'
        )
        parser.add_argument(
            '--filme',
            type=int,
            required=True,
            help='ID do filme'
        )
        parser.add_argument(
            '--inicio',
            type=str,
            required=True,
            help='Data e hora de início (YYYY-MM-DD HH:MM)'
        )
        parser.add_argument(
            '--fim',
            type=str,
            required=True,
            help='Data e hora de fim (YYYY-MM-DD HH:MM)'
        )
        parser.add_argument(
            '--versao',
            type=str,
            default='PT',
            help='Versão da sessão (PT, EN, etc.)'
        )
        parser.add_argument(
            '--preco',
            type=float,
            default=8.50,
            help='Preço da sessão'
        )

    def handle(self, *args, **options):
        try:
            # Validar entrada
            sala_id = options['sala']
            filme_id = options['filme']
            versao = options['versao']
            preco = options['preco']

            # Verificar se sala existe
            try:
                sala = Salas.objects.get(salaid=sala_id)
                self.stdout.write(f'Sala encontrada: {sala.nomesala} (Capacidade: {sala.capacidade})')
            except Salas.DoesNotExist:
                raise CommandError(f'Sala com ID {sala_id} não encontrada')

            # Verificar se filme existe
            try:
                filme = Filmes.objects.get(filmeid=filme_id)
                self.stdout.write(f'Filme encontrado: {filme.titulo}')
            except Filmes.DoesNotExist:
                raise CommandError(f'Filme com ID {filme_id} não encontrado')

            # Converter strings de data para datetime
            try:
                inicio = datetime.strptime(options['inicio'], '%Y-%m-%d %H:%M')
                fim = datetime.strptime(options['fim'], '%Y-%m-%d %H:%M')
            except ValueError:
                raise CommandError('Formato de data inválido. Use YYYY-MM-DD HH:MM')

            # Validar datas
            if inicio >= fim:
                raise CommandError('A data de início deve ser anterior à data de fim')

            if inicio < timezone.now().replace(tzinfo=None):
                self.stdout.write(
                    self.style.WARNING('Aviso: A sessão está sendo criada no passado')
                )

            # Mostrar resumo
            self.stdout.write('\n=== RESUMO DA SESSÃO ===')
            self.stdout.write(f'Sala: {sala.nomesala} (ID: {sala_id})')
            self.stdout.write(f'Filme: {filme.titulo} (ID: {filme_id})')
            self.stdout.write(f'Início: {inicio.strftime("%d/%m/%Y %H:%M")}')
            self.stdout.write(f'Fim: {fim.strftime("%d/%m/%Y %H:%M")}')
            self.stdout.write(f'Versão: {versao}')
            self.stdout.write(f'Preço: €{preco:.2f}')

            duracao = fim - inicio
            horas = duracao.total_seconds() // 3600
            minutos = (duracao.total_seconds() % 3600) // 60
            self.stdout.write(f'Duração: {int(horas)}h{int(minutos):02d}m')

            # Criar sessão usando a procedure
            self.stdout.write('\nCriando sessão...')
            
            sessao_id = CinemaProcedures.criar_sessao(
                sala_id, filme_id, inicio, fim, versao, preco
            )

            self.stdout.write(
                self.style.SUCCESS(f'✓ Sessão criada com sucesso! ID: {sessao_id}')
            )

            # Mostrar lugares disponíveis
            lugares = CinemaProcedures.obter_lugares_disponiveis(sessao_id)
            lugares_disponiveis = sum(1 for lugar in lugares if lugar['disponivel'])
            
            self.stdout.write(f'Lugares disponíveis: {lugares_disponiveis}/{len(lugares)}')

        except Exception as e:
            if 'Conflito de horário' in str(e):
                # Buscar sessões conflitantes para informar ao usuário
                self.stdout.write(
                    self.style.ERROR(f'Erro: {str(e)}')
                )
                self.mostrar_sessoes_conflitantes(sala_id, inicio, fim)
            else:
                raise CommandError(f'Erro ao criar sessão: {str(e)}')

    def mostrar_sessoes_conflitantes(self, sala_id, inicio, fim):
        """Mostra sessões que conflitam com o horário desejado."""
        from bd2ap1.models import Sessoes
        
        sessoes_conflitantes = Sessoes.objects.filter(
            salaid=sala_id,
            fim__gt=inicio,
            inicio__lt=fim
        ).select_related('filmeid')

        if sessoes_conflitantes:
            self.stdout.write('\n--- SESSÕES CONFLITANTES ---')
            for sessao in sessoes_conflitantes:
                self.stdout.write(
                    f'• {sessao.filmeid.titulo if sessao.filmeid else "N/A"} - '
                    f'{sessao.inicio.strftime("%d/%m/%Y %H:%M")} às '
                    f'{sessao.fim.strftime("%H:%M")} (ID: {sessao.sessaoid})'
                )
        
        self.stdout.write('\nSugestões:')
        self.stdout.write('• Verifique os horários disponíveis na sala')
        self.stdout.write('• Considere usar uma sala diferente') 
        self.stdout.write('• Ajuste o horário da sessão')
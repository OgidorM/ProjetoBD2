# bd2ap1/management/commands/vender_bilhetes.py
from django.core.management.base import BaseCommand, CommandError
from bd2ap1.procedimentos import CinemaProcedures
from bd2ap1.models import Clientes, Funcionarios, Sessoes, Lugares
from datetime import datetime


class Command(BaseCommand):
    help = 'Processa venda de bilhetes usando a procedure SQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cliente',
            type=int,
            required=True,
            help='ID do cliente'
        )
        parser.add_argument(
            '--funcionario',
            type=int,
            required=True,
            help='ID do funcionário'
        )
        parser.add_argument(
            '--sessao',
            type=int,
            required=True,
            help='ID da sessão'
        )
        parser.add_argument(
            '--lugares',
            type=str,
            required=True,
            help='IDs dos lugares separados por vírgula (ex: 1,2,3)'
        )
        parser.add_argument(
            '--mostrar-lugares',
            action='store_true',
            help='Mostra lugares disponíveis antes da venda'
        )

    def handle(self, *args, **options):
        try:
            # Validar entrada
            cliente_id = options['cliente']
            funcionario_id = options['funcionario']
            sessao_id = options['sessao']
            lugares_str = options['lugares']
            mostrar_lugares = options['mostrar_lugares']

            # Converter lugares para lista de inteiros
            try:
                lugares_ids = [int(x.strip()) for x in lugares_str.split(',')]
            except ValueError:
                raise CommandError('IDs de lugares inválidos. Use números separados por vírgula.')

            # Verificar se cliente existe
            try:
                cliente = Clientes.objects.get(clienteid=cliente_id)
                self.stdout.write(f'Cliente: {cliente.nomecliente} (ID: {cliente_id})')
            except Clientes.DoesNotExist:
                raise CommandError(f'Cliente com ID {cliente_id} não encontrado')

            # Verificar se funcionário existe
            try:
                funcionario = Funcionarios.objects.get(funcionarioid=funcionario_id)
                self.stdout.write(f'Funcionário: {funcionario.nomefuncionario} (ID: {funcionario_id})')
            except Funcionarios.DoesNotExist:
                raise CommandError(f'Funcionário com ID {funcionario_id} não encontrado')

            # Verificar se sessão existe
            try:
                sessao = Sessoes.objects.select_related('filmeid', 'salaid').get(sessaoid=sessao_id)
                self.stdout.write(f'Sessão: {sessao.filmeid.titulo if sessao.filmeid else "N/A"}')
                self.stdout.write(f'Sala: {sessao.salaid.nomesala if sessao.salaid else "N/A"}')
                self.stdout.write(f'Horário: {sessao.inicio.strftime("%d/%m/%Y %H:%M")}')
                self.stdout.write(f'Preço: €{sessao.precosessao:.2f}')
            except Sessoes.DoesNotExist:
                raise CommandError(f'Sessão com ID {sessao_id} não encontrada')

            # Mostrar lugares disponíveis se solicitado
            if mostrar_lugares:
                self.mostrar_mapa_lugares(sessao_id)

            # Verificar se os lugares existem e obter informações
            lugares_info = []
            for lugar_id in lugares_ids:
                try:
                    lugar = Lugares.objects.select_related('salaid').get(lugarid=lugar_id)
                    # Verificar se o lugar pertence à sala da sessão
                    if lugar.salaid != sessao.salaid:
                        raise CommandError(f'Lugar {lugar_id} não pertence à sala da sessão')
                    lugares_info.append(lugar)
                except Lugares.DoesNotExist:
                    raise CommandError(f'Lugar com ID {lugar_id} não encontrado')

            # Mostrar resumo da venda
            self.stdout.write('\n=== RESUMO DA VENDA ===')
            self.stdout.write(f'Cliente: {cliente.nomecliente}')
            self.stdout.write(f'Funcionário: {funcionario.nomefuncionario}')
            self.stdout.write(f'Filme: {sessao.filmeid.titulo if sessao.filmeid else "N/A"}')
            self.stdout.write(f'Sessão: {sessao.inicio.strftime("%d/%m/%Y %H:%M")}')
            self.stdout.write(f'Lugares:')
            
            total_preco = 0
            for lugar in lugares_info:
                self.stdout.write(f'  • Fila {lugar.fila}, Lugar {lugar.numero} (ID: {lugar.lugarid})')
                total_preco += float(sessao.precosessao)
            
            self.stdout.write(f'Total: €{total_preco:.2f}')

            # Processar venda usando a procedure
            self.stdout.write('\nProcessando venda...')
            
            venda_id = CinemaProcedures.processar_venda_bilhetes(
                cliente_id, funcionario_id, sessao_id, lugares_ids
            )

            self.stdout.write(
                self.style.SUCCESS(f'✓ Venda processada com sucesso! ID da venda: {venda_id}')
            )

            # Mostrar lugares restantes disponíveis
            lugares_disponiveis = CinemaProcedures.obter_lugares_disponiveis(sessao_id)
            disponiveis = sum(1 for lugar in lugares_disponiveis if lugar['disponivel'])
            total_lugares = len(lugares_disponiveis)
            
            self.stdout.write(f'Lugares ainda disponíveis: {disponiveis}/{total_lugares}')
            
            if disponiveis == 0:
                self.stdout.write(self.style.WARNING('⚠ Sessão esgotada!'))

        except Exception as e:
            if 'já está ocupado' in str(e):
                self.stdout.write(self.style.ERROR(f'Erro: {str(e)}'))
                self.mostrar_lugares_ocupados(sessao_id, lugares_ids)
            elif 'Capacidade máxima' in str(e):
                self.stdout.write(self.style.ERROR(f'Erro: {str(e)}'))
                self.mostrar_mapa_lugares(sessao_id)
            else:
                raise CommandError(f'Erro ao processar venda: {str(e)}')

    def mostrar_mapa_lugares(self, sessao_id):
        """Mostra o mapa de lugares da sessão."""
        lugares = CinemaProcedures.obter_lugares_disponiveis(sessao_id)
        
        if not lugares:
            self.stdout.write('Nenhum lugar encontrado para esta sessão.')
            return

        self.stdout.write('\n=== MAPA DE LUGARES ===')
        self.stdout.write('✓ = Disponível  ✗ = Ocupado')
        
        # Agrupar por fila
        filas = {}
        for lugar in lugares:
            fila = lugar['fila']
            if fila not in filas:
                filas[fila] = []
            filas[fila].append(lugar)

        # Ordenar filas e lugares
        for fila in sorted(filas.keys()):
            lugares_fila = sorted(filas[fila], key=lambda x: x['numero'])
            status_str = ''
            for lugar in lugares_fila:
                status = '✓' if lugar['disponivel'] else '✗'
                status_str += f'{lugar["numero"]:2d}{status} '
            
            self.stdout.write(f'Fila {fila}: {status_str}')

        # Estatísticas
        disponiveis = sum(1 for lugar in lugares if lugar['disponivel'])
        ocupados = len(lugares) - disponiveis
        self.stdout.write(f'\nDisponíveis: {disponiveis} | Ocupados: {ocupados} | Total: {len(lugares)}')

    def mostrar_lugares_ocupados(self, sessao_id, lugares_tentativa):
        """Mostra quais dos lugares solicitados estão ocupados."""
        lugares = CinemaProcedures.obter_lugares_disponiveis(sessao_id)
        lugares_dict = {lugar['lugarid']: lugar for lugar in lugares}
        
        self.stdout.write('\n--- STATUS DOS LUGARES SOLICITADOS ---')
        for lugar_id in lugares_tentativa:
            if lugar_id in lugares_dict:
                lugar = lugares_dict[lugar_id]
                if lugar['disponivel']:
                    status = 'DISPONÍVEL'
                    style = self.style.SUCCESS
                else:
                    status = 'OCUPADO'
                    style = self.style.ERROR
                
                self.stdout.write(
                    style(f'Lugar {lugar_id} (Fila {lugar["fila"]}, Nº {lugar["numero"]}): {status}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Lugar {lugar_id}: NÃO ENCONTRADO')
                )
        
        # Sugerir lugares alternativos
        lugares_disponiveis = [l for l in lugares if l['disponivel']]
        if lugares_disponiveis:
            self.stdout.write('\n--- LUGARES ALTERNATIVOS DISPONÍVEIS ---')
            for i, lugar in enumerate(lugares_disponiveis[:10]):  # Mostrar até 10
                self.stdout.write(
                    f'ID {lugar["lugarid"]} - Fila {lugar["fila"]}, Lugar {lugar["numero"]}'
                )
            
            if len(lugares_disponiveis) > 10:
                self.stdout.write(f'... e mais {len(lugares_disponiveis) - 10} lugares disponíveis.')
        else:
            self.stdout.write(self.style.WARNING('\nNenhum lugar disponível nesta sessão.'))
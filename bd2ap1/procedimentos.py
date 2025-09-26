# bd2ap1/procedimentos.py
"""
Módulo com procedures e functions personalizadas para o sistema de cinema.
Este módulo fornece uma interface Python para as procedures e functions SQL criadas.
"""

from django.db import connection
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime
import logging

logger = logging.getLogger(__name__)


class CinemaProcedures:
    """Classe para executar procedures e functions relacionadas ao sistema de cinema."""
    
    @staticmethod
    def criar_sessao(sala_id: int, filme_id: int, inicio: datetime, fim: datetime, 
                     versao: str, preco_sessao: float) -> int:
        """
        Cria uma nova sessão validando conflitos de horário.
        
        Args:
            sala_id: ID da sala
            filme_id: ID do filme
            inicio: Data/hora de início
            fim: Data/hora de fim
            versao: Versão (PT, EN, etc.)
            preco_sessao: Preço da sessão
            
        Returns:
            ID da sessão criada
            
        Raises:
            Exception: Se houver conflito de horário
        """
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT criar_sessao(%s, %s, %s, %s, %s, %s)",
                [sala_id, filme_id, inicio, fim, versao, preco_sessao]
            )
            result = cursor.fetchone()
            return result[0] if result else None
    
    @staticmethod
    def processar_venda_bilhetes(cliente_id: int, funcionario_id: int, 
                                sessao_id: int, lugares: List[int]) -> int:
        """
        Processa uma venda de bilhetes para múltiplos lugares.
        
        Args:
            cliente_id: ID do cliente
            funcionario_id: ID do funcionário
            sessao_id: ID da sessão
            lugares: Lista de IDs dos lugares
            
        Returns:
            ID da venda criada
            
        Raises:
            Exception: Se algum lugar já estiver ocupado
        """
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT processar_venda_bilhetes(%s, %s, %s, %s)",
                [cliente_id, funcionario_id, sessao_id, lugares]
            )
            result = cursor.fetchone()
            return result[0] if result else None
    
    @staticmethod
    def calcular_receita_periodo(data_inicio: date, data_fim: date, 
                                cinema_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Calcula a receita por período para um ou todos os cinemas.
        
        Args:
            data_inicio: Data de início do período
            data_fim: Data de fim do período
            cinema_id: ID do cinema (opcional, None para todos)
            
        Returns:
            Lista com dados de receita por cinema
        """
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM calcular_receita_periodo(%s, %s, %s)",
                [data_inicio, data_fim, cinema_id]
            )
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @staticmethod
    def obter_lugares_disponiveis(sessao_id: int) -> List[Dict[str, Any]]:
        """
        Obtém a disponibilidade de lugares para uma sessão.
        
        Args:
            sessao_id: ID da sessão
            
        Returns:
            Lista com informações dos lugares e disponibilidade
        """
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM obter_lugares_disponiveis(%s)",
                [sessao_id]
            )
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @staticmethod
    def limpar_sessoes_antigas(dias: int = 90) -> int:
        """
        Remove sessões finalizadas antigas.
        
        Args:
            dias: Número de dias (default: 90)
            
        Returns:
            Número de sessões removidas
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT limpar_sessoes_antigas(%s)", [dias])
            result = cursor.fetchone()
            return result[0] if result else 0
    
    @staticmethod
    def relatorio_mensal(mes: int, ano: int, cinema_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Gera relatório de desempenho mensal.
        
        Args:
            mes: Mês (1-12)
            ano: Ano
            cinema_id: ID do cinema (opcional)
            
        Returns:
            Lista com dados do relatório mensal
        """
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM relatorio_mensal(%s, %s, %s)",
                [mes, ano, cinema_id]
            )
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


class CinemaViews:
    """Classe para consultar as views criadas no sistema."""
    
    @staticmethod
    def sessoes_completas(filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Consulta a view de sessões completas com informações detalhadas.
        
        Args:
            filtros: Dicionário com filtros opcionais (ex: {'cinema': 'Nome Cinema'})
            
        Returns:
            Lista com dados das sessões completas
        """
        sql = "SELECT * FROM v_sessoes_completas"
        params = []
        
        if filtros:
            conditions = []
            if 'cinema' in filtros:
                conditions.append("nomecinema ILIKE %s")
                params.append(f"%{filtros['cinema']}%")
            if 'data' in filtros:
                conditions.append("DATE(inicio) = %s")
                params.append(filtros['data'])
            if 'filme' in filtros:
                conditions.append("filme ILIKE %s")
                params.append(f"%{filtros['filme']}%")
            
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
        
        sql += " ORDER BY inicio"
        
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @staticmethod
    def vendas_detalhadas(filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Consulta a view de vendas detalhadas.
        
        Args:
            filtros: Dicionário com filtros opcionais
            
        Returns:
            Lista com dados das vendas detalhadas
        """
        sql = "SELECT * FROM v_vendas_detalhadas"
        params = []
        
        if filtros:
            conditions = []
            if 'data_inicio' in filtros and 'data_fim' in filtros:
                conditions.append("data BETWEEN %s AND %s")
                params.extend([filtros['data_inicio'], filtros['data_fim']])
            if 'cinema' in filtros:
                conditions.append("nomecinema ILIKE %s")
                params.append(f"%{filtros['cinema']}%")
            if 'estado' in filtros:
                conditions.append("estadovenda = %s")
                params.append(filtros['estado'])
            
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
        
        sql += " ORDER BY data DESC, vendaid DESC"
        
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @staticmethod
    def filmes_popularidade(limite: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Consulta o ranking de filmes por popularidade.
        
        Args:
            limite: Número máximo de filmes a retornar
            
        Returns:
            Lista com dados dos filmes ordenados por popularidade
        """
        sql = "SELECT * FROM v_filmes_popularidade"
        if limite:
            sql += f" LIMIT {limite}"
        
        with connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @staticmethod
    def ocupacao_salas() -> List[Dict[str, Any]]:
        """
        Consulta a ocupação das salas.
        
        Returns:
            Lista com dados de ocupação das salas
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM v_ocupacao_salas")
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


# Funções de conveniência para uso direto
def criar_sessao_cinema(sala_id: int, filme_id: int, inicio: datetime, 
                       fim: datetime, versao: str = "PT", preco: float = 8.50) -> int:
    """Função de conveniência para criar uma sessão."""
    return CinemaProcedures.criar_sessao(sala_id, filme_id, inicio, fim, versao, preco)


def vender_bilhetes(cliente_id: int, funcionario_id: int, sessao_id: int, 
                   lugares: List[int]) -> int:
    """Função de conveniência para vender bilhetes."""
    return CinemaProcedures.processar_venda_bilhetes(cliente_id, funcionario_id, sessao_id, lugares)


def lugares_livres(sessao_id: int) -> List[Dict[str, Any]]:
    """Função de conveniência para obter lugares disponíveis."""
    return CinemaProcedures.obter_lugares_disponiveis(sessao_id)


def receita_mensal(mes: int, ano: int, cinema_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Função de conveniência para relatório mensal."""
    return CinemaProcedures.relatorio_mensal(mes, ano, cinema_id)


def sessoes_hoje() -> List[Dict[str, Any]]:
    """Função de conveniência para sessões de hoje."""
    return CinemaViews.sessoes_completas({'data': date.today()})


def top_filmes(limite: int = 10) -> List[Dict[str, Any]]:
    """Função de conveniência para top filmes."""
    return CinemaViews.filmes_popularidade(limite)
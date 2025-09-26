# SISTEMA DE CINEMA - PROCEDURES E VIEWS
# ====================================

Este documento descreve as procedures, views, functions e triggers implementadas no sistema de cinema, bem como como utilizá-las através do Django.

## VIEWS IMPLEMENTADAS

### 1. v_sessoes_completas
Informações completas sobre sessões incluindo ocupação e disponibilidade.

**Campos:**
- sessaoid, nomecinema, nomesala, filme, categoria
- inicio, fim, versao, estadosessao, precosessao
- capacidade, bilhetes_vendidos, lugares_disponiveis, taxa_ocupacao

### 2. v_vendas_detalhadas
Análise detalhada das vendas com informações de clientes, funcionários e produtos.

**Campos:**
- vendaid, data, nomecliente, nomefuncionario, nomecinema
- estadovenda, totalvenda, total_linhas, total_bilhetes, produtos_vendidos

### 3. v_filmes_popularidade
Ranking de filmes por popularidade baseado em vendas de bilhetes.

**Campos:**
- filmeid, titulo, nomecategoria, nomecinema, ranking_filme
- total_sessoes, total_bilhetes_vendidos, receita_total, avaliacao_media

### 4. v_ocupacao_salas
Análise de ocupação de salas por cinema.

**Campos:**
- salaid, nomecinema, nomesala, capacidade, tiposala
- total_sessoes, total_bilhetes_vendidos, taxa_ocupacao_media

## PROCEDURES E FUNCTIONS

### 1. criar_sessao(sala_id, filme_id, inicio, fim, versao, preco)
Cria uma nova sessão validando conflitos de horário.

**Exemplo de uso em Python:**
```python
from bd2ap1.procedimentos import CinemaProcedures
from datetime import datetime

sessao_id = CinemaProcedures.criar_sessao(
    sala_id=1,
    filme_id=5,
    inicio=datetime(2024, 10, 15, 20, 0),
    fim=datetime(2024, 10, 15, 22, 30),
    versao='PT',
    preco_sessao=8.50
)
```

### 2. processar_venda_bilhetes(cliente_id, funcionario_id, sessao_id, lugares[])
Processa venda de bilhetes para múltiplos lugares.

**Exemplo de uso em Python:**
```python
venda_id = CinemaProcedures.processar_venda_bilhetes(
    cliente_id=1,
    funcionario_id=2,
    sessao_id=10,
    lugares=[15, 16, 17]  # IDs dos lugares
)
```

### 3. calcular_receita_periodo(data_inicio, data_fim, cinema_id?)
Calcula receita por período para um ou todos os cinemas.

**Exemplo de uso em Python:**
```python
from datetime import date

receita = CinemaProcedures.calcular_receita_periodo(
    data_inicio=date(2024, 10, 1),
    data_fim=date(2024, 10, 31),
    cinema_id=None  # Todos os cinemas
)
```

### 4. obter_lugares_disponiveis(sessao_id)
Retorna disponibilidade de lugares para uma sessão.

**Exemplo de uso em Python:**
```python
lugares = CinemaProcedures.obter_lugares_disponiveis(sessao_id=10)
disponiveis = [l for l in lugares if l['disponivel']]
```

### 5. relatorio_mensal(mes, ano, cinema_id?)
Gera relatório de desempenho mensal.

**Exemplo de uso em Python:**
```python
relatorio = CinemaProcedures.relatorio_mensal(
    mes=10,
    ano=2024,
    cinema_id=1
)
```

### 6. limpar_sessoes_antigas(dias)
Remove sessões finalizadas antigas.

**Exemplo de uso em Python:**
```python
removidas = CinemaProcedures.limpar_sessoes_antigas(dias=90)
```

## COMANDOS DE GERENCIAMENTO DJANGO

### 1. Aplicar as migrações
```bash
python manage.py migrate
```

### 2. Criar uma sessão
```bash
python manage.py criar_sessao --sala 1 --filme 5 --inicio "2024-10-15 20:00" --fim "2024-10-15 22:30" --versao PT --preco 8.50
```

### 3. Vender bilhetes
```bash
python manage.py vender_bilhetes --cliente 1 --funcionario 2 --sessao 10 --lugares "15,16,17"
```

### 4. Gerar relatórios
```bash
# Relatório mensal
python manage.py relatorio_cinema --tipo mensal --mes 10 --ano 2024

# Relatório de receita
python manage.py relatorio_cinema --tipo receita --data-inicio "2024-10-01" --data-fim "2024-10-31"

# Ranking de filmes
python manage.py relatorio_cinema --tipo filmes

# Ocupação de salas
python manage.py relatorio_cinema --tipo ocupacao

# Relatório de sessões
python manage.py relatorio_cinema --tipo sessoes --cinema 1
```

### 5. Manutenção do sistema
```bash
# Verificar integridade
python manage.py manutencao_cinema --acao verificar_integridade

# Estatísticas gerais
python manage.py manutencao_cinema --acao estatisticas

# Limpar sessões antigas (requer confirmação)
python manage.py manutencao_cinema --acao limpar_sessoes --dias 90 --confirmar
```

## USO DAS VIEWS EM PYTHON

### Consultando views diretamente
```python
from bd2ap1.procedimentos import CinemaViews

# Sessões completas de hoje
sessoes_hoje = CinemaViews.sessoes_completas({'data': date.today()})

# Vendas de um período
vendas = CinemaViews.vendas_detalhadas({
    'data_inicio': date(2024, 10, 1),
    'data_fim': date(2024, 10, 31),
    'cinema': 'Cinema Central'
})

# Top 10 filmes
top_filmes = CinemaViews.filmes_popularidade(limite=10)

# Ocupação de salas
ocupacao = CinemaViews.ocupacao_salas()
```

### Funções de conveniência
```python
from bd2ap1.procedimentos import (
    criar_sessao_cinema, vender_bilhetes, lugares_livres,
    receita_mensal, sessoes_hoje, top_filmes
)

# Criar sessão
sessao_id = criar_sessao_cinema(
    sala_id=1, filme_id=5,
    inicio=datetime(2024, 10, 15, 20, 0),
    fim=datetime(2024, 10, 15, 22, 30)
)

# Vender bilhetes
venda_id = vender_bilhetes(
    cliente_id=1, funcionario_id=2,
    sessao_id=sessao_id, lugares=[15, 16]
)

# Ver lugares disponíveis
lugares = lugares_livres(sessao_id)

# Relatório mensal
relatorio = receita_mensal(mes=10, ano=2024)

# Sessões de hoje
sessoes = sessoes_hoje()

# Top filmes
filmes = top_filmes(limite=5)
```

## TRIGGERS IMPLEMENTADOS

### 1. trigger_atualizar_ranking_filme
Atualiza automaticamente o ranking de filmes baseado na venda de bilhetes.
- Acionado: AFTER INSERT ON bilhetes
- Função: Calcula novo ranking baseado no total de bilhetes vendidos

### 2. trigger_validar_capacidade
Valida se a capacidade da sala não foi excedida antes de inserir bilhete.
- Acionado: BEFORE INSERT ON bilhetes
- Função: Verifica se ainda há lugares disponíveis na sessão

## ÍNDICES CRIADOS

Para otimização de performance:
- idx_sessoes_data: Índice na coluna inicio da tabela sessoes
- idx_vendas_data: Índice na coluna data da tabela vendas
- idx_bilhetes_sessao: Índice na coluna sessaoid da tabela bilhetes
- idx_filmes_cinema: Índice na coluna cinemaid da tabela filmes
- idx_avaliacoes_vendas: Índice na coluna vendaid da tabela avaliacoes

## EXEMPLOS DE CONSULTAS SQL DIRETAS

### Consultar sessões completas
```sql
SELECT * FROM v_sessoes_completas 
WHERE DATE(inicio) = CURRENT_DATE 
ORDER BY inicio;
```

### Criar uma sessão
```sql
SELECT criar_sessao(1, 5, '2024-10-15 20:00:00', '2024-10-15 22:30:00', 'PT', 8.50);
```

### Vender bilhetes
```sql
SELECT processar_venda_bilhetes(1, 2, 10, ARRAY[15, 16, 17]);
```

### Ver lugares disponíveis
```sql
SELECT * FROM obter_lugares_disponiveis(10);
```

### Relatório de receita
```sql
SELECT * FROM calcular_receita_periodo('2024-10-01', '2024-10-31', NULL);
```

### Relatório mensal
```sql
SELECT * FROM relatorio_mensal(10, 2024);
```

### Limpeza de sessões antigas
```sql
SELECT limpar_sessoes_antigas(90);
```

## NOTAS IMPORTANTES

1. **Validações**: As procedures incluem validações para evitar conflitos de horário e overbooking.

2. **Transações**: Todas as procedures usam transações implícitas para garantir consistência.

3. **Triggers**: Os triggers são executados automaticamente e mantêm a integridade dos dados.

4. **Performance**: Os índices foram criados nas colunas mais consultadas para otimizar performance.

5. **Manutenção**: Use regularmente os comandos de manutenção para verificar integridade e limpar dados antigos.

6. **Logs**: Erros das procedures são registrados e podem ser consultados nos logs do Django.

7. **Backup**: Faça backup regular do banco de dados antes de executar operações de limpeza.
import pytest
from django.db import connections


# ==============================================================
#  TESTES AOS PROCEDIMENTOS CRUD DO SISTEMA DE CINEMA
#  (utilizam transações BEGIN / ROLLBACK para não persistir dados)
# ==============================================================


# 1️⃣ Inserir Filme
@pytest.mark.django_db(transaction=True)
def test_inserir_filme_ok():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    cur.execute("""
        CALL inserir_filme(
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
    """, [
        1,  # categoriaid
        1,  # cinemaid
        'Filme Teste Pytest',
        '2025-01-01',
        120,
        'Produtora X',
        '2025-12-31',
        'PT',
        'Sinopse teste',
        1,  # classificacaoid
        0.0
    ])
    cur.execute("SELECT COUNT(*) FROM filmes WHERE titulo = %s;", ['Filme Teste Pytest'])
    count = cur.fetchone()[0]
    assert count == 1, "Falha ao inserir filme"
    cur.execute("ROLLBACK;")


# 2️⃣ Inserir Sessão
@pytest.mark.django_db(transaction=True)
def test_inserir_sessao_ok():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    cur.execute("""
        CALL inserir_sessao(
            %s, %s, %s, %s, %s, %s, %s
        );
    """, [
        1,  # salaid
        1,  # filmeid
        '2025-11-10 15:00:00',
        '2025-11-10 17:00:00',
        '2D',
        'Agendada',
        10.00
    ])
    cur.execute("""
        SELECT COUNT(*) FROM sessoes
        WHERE salaid = %s AND filmeid = %s
          AND inicio = %s;
    """, [1, 1, '2025-11-10 15:00:00'])
    count = cur.fetchone()[0]
    assert count == 1, "Falha ao inserir sessão"
    cur.execute("ROLLBACK;")


# 3️⃣ Inserir Produto
@pytest.mark.django_db(transaction=True)
def test_inserir_produto_ok():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    cur.execute("CALL inserir_produto(%s, %s, %s, %s);", [
        'Produto Teste', 9.99, 100, True
    ])
    cur.execute("SELECT COUNT(*) FROM produtos WHERE nomeproduto = %s;", ['Produto Teste'])
    count = cur.fetchone()[0]
    assert count == 1, "Falha ao inserir produto"
    cur.execute("ROLLBACK;")


# 4️⃣ Inserir Avaliação
@pytest.mark.django_db(transaction=True)
def test_inserir_avaliacao_ok():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    # assumindo que existe vendaid=1 com estado 'Concluída'
    cur.execute("""
        CALL inserir_avaliacao(%s, %s, %s, %s, %s, %s);
    """, [
        1, 'Avaliação Teste', 5, 4, 5, 'Comentário Pytest'
    ])
    cur.execute("""
        SELECT COUNT(*) FROM avaliacoes
        WHERE vendaid = %s AND tituloavaliacao = %s;
    """, [1, 'Avaliação Teste'])
    count = cur.fetchone()[0]
    assert count == 1, "Falha ao inserir avaliação"
    cur.execute("ROLLBACK;")


# 5️⃣ Inserir Cinema
@pytest.mark.django_db(transaction=True)
def test_inserir_cinema_ok():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    cur.execute("""
        CALL inserir_cinema(%s, %s, %s, %s, %s, %s, %s);
    """, [
        'Cinema Teste',
        'cinema@teste.pt',
        '912345678',
        'Rua Central, 10',
        '1234-567',
        'Cidade Teste',
        0.0
    ])
    cur.execute("""
        SELECT COUNT(*) FROM cinemas
        WHERE nomecinema = %s AND localidadecinema = %s;
    """, ['Cinema Teste', 'Cidade Teste'])
    count = cur.fetchone()[0]
    assert count == 1, "Falha ao inserir cinema"
    cur.execute("ROLLBACK;")


# 6️⃣ Inserir Cliente
@pytest.mark.django_db(transaction=True)
def test_inserir_cliente_ok():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    cur.execute("""
        CALL inserir_cliente(%s, %s, %s, %s, %s, %s, %s, %s);
    """, [
        'Cliente Teste',
        'cliente@teste.pt',
        '912345679',
        '2000-01-01',
        'Rua das Rosas, 20',
        '2345-678',
        'Localidade Z',
        '123456789'
    ])
    cur.execute("""
        SELECT COUNT(*) FROM clientes
        WHERE emailcliente = %s AND nif = %s;
    """, ['cliente@teste.pt', '123456789'])
    count = cur.fetchone()[0]
    assert count == 1, "Falha ao inserir cliente"
    cur.execute("ROLLBACK;")


# 7️⃣ Inserir Sala
@pytest.mark.django_db(transaction=True)
def test_inserir_sala_ok():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    cur.execute("""
        CALL inserir_sala(%s, %s, %s, %s);
    """, [
        1, 'Sala Teste', 150, 'Standard'
    ])
    cur.execute("""
        SELECT COUNT(*) FROM salas
        WHERE cinemaid = %s AND nomesala = %s;
    """, [1, 'Sala Teste'])
    count = cur.fetchone()[0]
    assert count == 1, "Falha ao inserir sala"
    cur.execute("ROLLBACK;")


# 8️⃣ Inserir Bilhete
@pytest.mark.django_db(transaction=True)
def test_inserir_bilhete_ok():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    # assumindo que lugarid=1 e sessaoid=1 existem
    cur.execute("""
        CALL inserir_bilhete(%s, %s, %s);
    """, [
        1, 1, 8.50
    ])
    cur.execute("""
        SELECT COUNT(*) FROM bilhetes
        WHERE lugarid = %s AND sessaoid = %s;
    """, [1, 1])
    count = cur.fetchone()[0]
    assert count == 1, "Falha ao inserir bilhete"
    cur.execute("ROLLBACK;")


import pytest
from django.db import connections
from datetime import datetime

pytestmark = pytest.mark.django_db(transaction=True)

# ============================================================
#  TESTES AOS PROCEDIMENTOS DO SISTEMA DE CINEMA
# ============================================================


def test_inserir_filme():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    try:
        titulo = f"Filme Teste {datetime.now().strftime('%H%M%S')}"

        cur.execute("""
            CALL inserir_filme(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, [
            1, 1, titulo,
            '2025-01-01', 120, 'Produtora X',
            '2025-12-31', 'PT', 'Sinopse de teste',
            1, 4.5
        ])

        cur.execute("SELECT COUNT(*) FROM filmes WHERE titulo = %s;", [titulo])
        count = cur.fetchone()[0]
        assert count == 1, "O filme não foi inserido corretamente."
        print("SUCESSO: o procedimento inserir_filme executou corretamente.")
    except Exception as e:
        pytest.fail(f"Falha ao executar inserir_filme. Detalhes: {e}")
    finally:
        cur.execute("ROLLBACK;")


def test_inserir_sessao():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    try:
        inicio = '2025-11-10 15:00:00'
        fim = '2025-11-10 17:00:00'

        cur.execute("""
            CALL inserir_sessao(%s, %s, %s, %s, %s, %s, %s);
        """, [1, 1, inicio, fim, '2D', 'Agendada', 9.50])

        cur.execute("""
            SELECT COUNT(*) FROM sessoes
            WHERE salaid = %s AND filmeid = %s AND inicio = %s;
        """, [1, 1, inicio])
        count = cur.fetchone()[0]
        assert count == 1, "A sessão não foi criada corretamente."
        print("SUCESSO: o procedimento inserir_sessao executou corretamente.")
    except Exception as e:
        pytest.fail(f"Falha ao executar inserir_sessao. Detalhes: {e}")
    finally:
        cur.execute("ROLLBACK;")


def test_inserir_produto():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    try:
        nome = f"Produto Teste {datetime.now().strftime('%H%M%S')}"
        cur.execute("CALL inserir_produto(%s, %s, %s, %s);", [nome, 8.99, 25, True])
        cur.execute("SELECT COUNT(*) FROM produtos WHERE nomeproduto = %s;", [nome])
        count = cur.fetchone()[0]
        assert count == 1, "O produto não foi inserido corretamente."
        print("SUCESSO: o procedimento inserir_produto executou corretamente.")
    except Exception as e:
        pytest.fail(f"Falha ao executar inserir_produto. Detalhes: {e}")
    finally:
        cur.execute("ROLLBACK;")


def test_inserir_avaliacao():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    try:
        cur.execute("""
            CALL inserir_avaliacao(%s, %s, %s, %s, %s, %s);
        """, [4, 'Avaliação Teste', 5, 4, 5, 'Comentário de teste'])

        cur.execute("SELECT COUNT(*) FROM avaliacoes WHERE vendaid = %s;", [4])
        count = cur.fetchone()[0]
        assert count == 1, "A avaliação não foi criada corretamente."
        print("SUCESSO: o procedimento inserir_avaliacao executou corretamente.")
    except Exception as e:
        pytest.fail(f"Falha ao executar inserir_avaliacao. Detalhes: {e}")
    finally:
        cur.execute("ROLLBACK;")


def test_inserir_cinema():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    try:
        nome = f"Cinema Teste {datetime.now().strftime('%H%M%S')}"
        cur.execute("""
            CALL inserir_cinema(%s, %s, %s, %s, %s, %s, %s);
        """, [nome, 'cinema@teste.pt', '911234567', 'Rua Central 1', '1234-567', 'Lisboa', 0.0])

        cur.execute("SELECT COUNT(*) FROM cinemas WHERE nomecinema = %s;", [nome])
        count = cur.fetchone()[0]
        assert count == 1, "O cinema não foi inserido corretamente."
        print("SUCESSO: o procedimento inserir_cinema executou corretamente.")
    except Exception as e:
        pytest.fail(f"Falha ao executar inserir_cinema. Detalhes: {e}")
    finally:
        cur.execute("ROLLBACK;")


def test_inserir_cliente():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    try:
        nif = f"{datetime.now().strftime('%H%M%S')}123"
        email = f"cliente{datetime.now().strftime('%H%M%S')}@teste.pt"
        cur.execute("""
            CALL inserir_cliente(%s, %s, %s, %s, %s, %s, %s, %s);
        """, ['Cliente Teste', email, '912345679', '2000-01-01', 'Rua das Rosas', '2345-678', 'Viseu', nif])

        cur.execute("SELECT COUNT(*) FROM clientes WHERE nif = %s;", [nif])
        count = cur.fetchone()[0]
        assert count == 1, "O cliente não foi inserido corretamente."
        print("SUCESSO: o procedimento inserir_cliente executou corretamente.")
    except Exception as e:
        pytest.fail(f"Falha ao executar inserir_cliente. Detalhes: {e}")
    finally:
        cur.execute("ROLLBACK;")


def test_inserir_sala():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    try:
        nome = f"Sala Teste {datetime.now().strftime('%H%M%S')}"
        cur.execute("CALL inserir_sala(%s, %s, %s, %s);", [1, nome, 150, 'Standard'])

        cur.execute("SELECT COUNT(*) FROM salas WHERE nomesala = %s;", [nome])
        count = cur.fetchone()[0]
        assert count == 1, "A sala não foi criada corretamente."
        print("SUCESSO: o procedimento inserir_sala executou corretamente.")
    except Exception as e:
        pytest.fail(f"Falha ao executar inserir_sala. Detalhes: {e}")
    finally:
        cur.execute("ROLLBACK;")


def test_inserir_bilhete():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    try:
        cur.execute("CALL inserir_bilhete(%s, %s, %s);", [3, 1, 8.50])

        cur.execute("SELECT COUNT(*) FROM bilhetes WHERE lugarid = %s AND sessaoid = %s;", [3, 1])
        count = cur.fetchone()[0]
        assert count == 1, "O bilhete não foi criado corretamente."

        cur.execute("SELECT lugarid FROM lugaressessao WHERE lugarid = %s;" , [3])
        lugar_sessao = cur.fetchone()[0]
        assert lugar_sessao.estado == 'Ocupado', "O estado do lugar não foi atualizado para 'Ocupado'."
        print("SUCESSO: o procedimento inserir_bilhete executou corretamente.")
    except Exception as e:
        pytest.fail(f"Falha ao executar inserir_bilhete. Detalhes: {e}")
    finally:
        cur.execute("ROLLBACK;")



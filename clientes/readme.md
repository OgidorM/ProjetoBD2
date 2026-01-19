# Módulo de Clientes (Clean Architecture)

Este módulo foi refatorado para seguir princípios de **Clean Architecture** e **SOLID**, separando a lógica de negócio do framework Django.

## Estrutura de Pastas

### 1. `core/` (Regra de Negócio)
Contém a lógica pura do sistema, agnóstica ao método de entrega (seja API ou HTML).
- **`services.py`**: A classe `ClienteService` orquestra as operações.
- **`dtos.py`**: Objetos de transferência de dados para garantir tipagem segura.

### 2. `data/` (Acesso a Dados)
Camada responsável por comunicar com o Banco de Dados.
- **`repositories.py`**: Centraliza as queries SQL e o `select_related`, evitando repetição de código nas Views.

### 3. `api/` (Interface REST)
Endpoints para clientes externos (React/Mobile).
- **`views.py`**: Recebe JSON e chama o `Service`.
- **`serializers.py`**: Validação de entrada.

### 4. Raiz (`views.py`, `forms.py`)
Mantida para o **Painel Administrativo (Backoffice)** legado, renderizando templates HTML, mas consumindo a mesma lógica do `core/services.py`.
# Cinema Management & Sales Platform (Django)

This project is a Django 5.x application modeling a cinema ecosystem: films, sessions, rooms, seats, ticketing, product sales (concessions), and customer evaluations. It now exposes a lightweight MVC-style (Controller-focused) layer for selected domain aggregates (`cinemas`, `clientes`, `funcionarios`) while preserving a clean internal layering (Models → Repositories → Services → Views/Controllers → Templates).

## Features

- Domain modeling for:
  - Categorias (movie categories)
  - Classificações Etárias (age ratings)
  - Cinemas, Salas (rooms), Lugares (seats)
  - Filmes (movies) with ranking + classification
  - Sessoes (showtimes) with pricing
  - Clientes & Funcionarios
  - Produtos (concession items) and Vendas / VendaLinhas (sales + line items)
  - Bilhetes (tickets) linked to Sessões & Lugares
  - Avaliações (customer feedback on a sale)
- Database constraints (check + unique) for data integrity
- Separation between core data model (`bd2ap1`) and UI-oriented front apps
- Clean layering with repository + service abstraction for selected domain apps
- Function-based MVC-style controllers (views) + CRUD + JSON output for Cinemas, Clients, Employees
- PostgreSQL as the configured database backend (SQLite file present but not used by default settings)

## Architecture Overview

Although Django follows MTV, we structure internal code in a style close to classic MVC + Clean Architecture for certain apps:

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Data Model | `bd2ap1/models.py` (+ proxy models in `cinemas/`, `clientes/`, `funcionarios/`) | Database schema & core entities |
| Repository | `*/repositories.py` | Encapsulate ORM reads, list/search/delete, create/update (added for consistency) |
| Service | `*/services.py` | Business logic & orchestration (no HTTP, no presentation) |
| Controller (View) | `*/views.py` (function-based) | Thin request handling: parse request → call service → render template / JSON |
| Presentation | `templates/<app_name>/*.html` | Minimal HTML templates (no business logic) |

### Why Repositories + Services?
- Repositories isolate query logic and provide a narrow interface (e.g. `list_all`, `search`, `update`).
- Services encapsulate mutation / domain rules (e.g. `update_rating`, generic `update` loops) and keep views free of business decisions.
- Views remain testable and thin (only flow + serialization concerns).

### Recently Added / Refactored
- Added `create()` and `update()` functions to repositories for `cinemas`, `clientes`, `funcionarios`.
- Refactored services to invoke repository create/update instead of direct model persistence.
- Added function-based CRUD + search views and templates for the three domains.
- Added optional JSON rendering via `?format=json` on list and detail endpoints.
- Added dedicated `/search/?q=...&limit=` JSON endpoints.
- Injected navigation and return buttons (Home / List / JSON) in templates.
- Updated home page (`core/index.html`) with quick access buttons.

## MVC-style Endpoints (Current)

All endpoints are mounted under project root (`b2da1/urls.py`).

### Cinemas
```
GET   /cinemas/                # HTML list (or JSON with ?format=json)
GET   /cinemas/search/?q=Term  # JSON search
GET   /cinemas/create/         # Form (create)
POST  /cinemas/create/         # Persist
GET   /cinemas/<id>/           # Detail (or JSON)
GET   /cinemas/<id>/edit/      # Edit form
POST  /cinemas/<id>/edit/      # Update
GET   /cinemas/<id>/delete/    # Confirm delete
POST  /cinemas/<id>/delete/    # Delete
```

### Clients (`clientes`)
```
GET   /clientes/               # List (HTML / JSON)
GET   /clientes/search/?q=...  # JSON search
GET   /clientes/create/        # Create form
POST  /clientes/create/        # Persist
GET   /clientes/<id>/          # Detail (HTML / JSON)
GET   /clientes/<id>/edit/
POST  /clientes/<id>/edit/
GET   /clientes/<id>/delete/
POST  /clientes/<id>/delete/
```

### Employees (`funcionarios`)
```
GET   /funcionarios/               # List (HTML / JSON)
GET   /funcionarios/search/?q=...  # JSON search
GET   /funcionarios/create/
POST  /funcionarios/create/
GET   /funcionarios/<id>/
GET   /funcionarios/<id>/edit/
POST  /funcionarios/<id>/edit/
GET   /funcionarios/<id>/delete/
POST  /funcionarios/<id>/delete/
```

### JSON Output Pattern
- Append `?format=json` to list or detail views for structured responses.
- Search endpoints always return JSON with: `{"query": ..., "count": <int>, "results": [ ... ]}`.

### Example JSON Calls
```
GET /cinemas/?format=json
GET /cinemas/1/?format=json
GET /cinemas/search/?q=cen&limit=5
GET /clientes/?format=json
GET /funcionarios/search/?q=mar
```

## Quick Usage Flow (Example)
```python
from cinemas import services as cinema_services

c = cinema_services.create(
    nomecinema="Cinema Centro",
    localidadecinema="Lisboa",
    ranking=4.5
)
cinema_services.update_rating(c.cinemaid, 4.9)
updated = cinema_services.get(c.cinemaid)
```

## Tech Stack

- Python 3.12+
- Django 5.2.6
- PostgreSQL 14+

## Project Structure (high level)

```
manage.py
b2da1/                 # Project config (settings, urls, wsgi/asgi)
bd2ap1/                # Core domain models & migrations
cinemas/               # MVC domain (proxy + repo + service + controller + templates)
clientes/              # MVC domain (proxy + repo + service + controller + templates)
funcionarios/          # MVC domain (proxy + repo + service + controller + templates)
<entity>_front/        # Legacy/front apps
templates/             # Global / shared templates
```

## Initial Setup

### 1. Clone & Enter Project
```
git clone <your-repo-url>
cd b2da1
```
### 2. Create & Activate Virtual Environment
```
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```
### 3. Install Dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
```
### 4. Configure PostgreSQL
```
psql -U postgres -c "CREATE DATABASE \"cinemaDB\";"
psql -U postgres -c "CREATE USER admin WITH PASSWORD 'admin';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE \"cinemaDB\" TO admin;"
```
(Adjust credentials or switch to SQLite for quick tests.)

### 5. Apply Migrations
```
python manage.py migrate
```
### 6. Create Superuser (optional)
```
python manage.py createsuperuser
```
### 7. Run Server
```
python manage.py runserver
```
Browse: http://127.0.0.1:8000/

## Data Model Highlights

| Entity | Key Fields | Notes |
|--------|------------|-------|
| Categorias | nomecategoria | Classification / genre of films |
| ClassificacoesEtarias | nomeclassificacao | Age rating (e.g. M/12) |
| Cinemas | localidadecinema, ranking | Ranking constrained 0–5 |
| Filmes | titulo, categoriaid, cinemaid, classificacaoetaria, ranking | Ranking constrained 0–5 |
| Salas | cinemaid, capacidade, tiposala | Rooms inside cinema |
| Lugares | (salaid,fila,numero) unique | Seat identity constraint |
| Sessoes | inicio, fim, filmeid, salaid | Showtimes |
| Clientes | nomecliente, emailcliente | Customers |
| Funcionarios | cinemaid, cargo, ranking | Staff, ranking 0–5 |
| Produtos | nomeproduto, precoproduto, stock | Concession items |
| Vendas | clienteid, funcionarioid, totalvenda | A sale transaction |
| VendaLinhas | vendaid, produtoid, quantidade | Line items |
| Bilhetes | sessaoid, lugarid, precobilhete | Ticket for session seat |
| Avaliacoes | venda (1:1) + ratings | Feedback per sale |

### Constraints / Integrity
- Ranking check constraints (0–5) for Cinemas, Filmes, Funcionarios.
- Unique (`salaid`, `fila`, `numero`) for Lugares.
- PROTECT FKs to avoid accidental cascading on reference data.

## Running Tests
```
python manage.py test
```
(Add tests in each app's `tests.py`.)

## Migrations Workflow
```
python manage.py makemigrations
python manage.py migrate
```

## Useful Commands
```
python manage.py shell
python manage.py check
python manage.py showmigrations
```

## Troubleshooting
| Issue | Possible Fix |
|-------|--------------|
| psycopg2 errors | Ensure PostgreSQL up & credentials correct |
| TemplateDoesNotExist | Check app in INSTALLED_APPS & path templates/app_name/file.html |
| relation does not exist | Run migrations |
| Invalid ranking | Validation or model constraint triggered |

## Improvement Ideas
- Base template + template inheritance for new MVC templates (currently minimal / duplicated markup)
- Flash messages on create/update/delete
- Pagination & ordering parameters on list endpoints
- DRF-based API layer
- Central error handling decorator for 404 mapping
- Environment variable driven settings

## License
Specify a license (e.g., MIT) if distributing publicly.

---
Happy building! This README now reflects the layered MVC-style additions (repositories + services + thin controllers) and newly exposed CRUD/JSON endpoints.

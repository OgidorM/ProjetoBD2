# Cinema Management & Sales Platform (Django)

This project is a Django 5.x application modeling a cinema ecosystem: films, sessions, rooms, seats, ticketing, product sales (concessions), and customer evaluations. It is organized into a core domain app (`bd2ap1`) that defines the database schema and several "front" apps that can provide views/forms per entity (e.g. `filmes_front`, `salas_front`, `vendas_front`, etc.).

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
- PostgreSQL as the configured database backend (SQLite file present but not used by default settings)

## Tech Stack

- Python 3.12+ (recommend 3.12; adjust if needed)
- Django 5.2.6
- PostgreSQL 14+ (any recent version should work)
- (Optional) SQLite for quick experimentation

## Project Structure (high level)

```
manage.py
b2da1/                # Project config (settings, urls, wsgi/asgi)
bd2ap1/                # Core domain models & migrations
<entity>_front/        # Front-end oriented Django apps (forms, views, templates)
templates/             # Global / shared templates
```

Each `*_front` app may provide forms, basic CRUD views, and templates associated with its domain entity.

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
Create a database and user that match `b2da1/settings.py` (or adjust settings):
```
psql -U postgres -c "CREATE DATABASE \"cinemaDB\";"
psql -U postgres -c "CREATE USER admin WITH PASSWORD 'admin';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE \"cinemaDB\" TO admin;"
```
If you change credentials, update `DATABASES` in `b2da1/settings.py`.

#### Alternative: Use SQLite (quick start)
Edit `b2da1/settings.py` and replace the `DATABASES` dict with:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 5. Apply Migrations
```
python manage.py migrate
```

### 6. Create Superuser (for /admin)
```
python manage.py createsuperuser
```

### 7. Run Development Server
```
python manage.py runserver
```
Visit: http://127.0.0.1:8000/ and http://127.0.0.1:8000/admin/

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
| VendaLinhas | vendaid, produtoid, quantidade | Line items, total_linha optional |
| Bilhetes | sessaoid, lugarid, precobilhete | Ticket for a seat in a session |
| Avaliacoes | OneToOne(Vendas) + ratings | Feedback per sale |

### Constraints / Integrity
- Check constraints enforce ranking ranges (0–5) for Cinemas, Filmes, Funcionarios.
- Unique constraint on Lugares: (`salaid`, `fila`, `numero`).
- `Avaliacoes.venda` is One-to-One (each sale may have at most one evaluation).
- Most foreign keys use `PROTECT` to avoid cascading deletes of core reference data.

## Running Tests
```
python manage.py test
```
Add tests to each app's `tests.py` or create packages as needed.

## Adding a New App
```
python manage.py startapp <name>_front
# Add to INSTALLED_APPS in b2da1/settings.py
```
Then create `urls.py`, views, templates, and include routes in the project root `urls.py`.

## Environment / Secrets
Current `settings.py` contains an inline `SECRET_KEY` and `DEBUG=True` for development only. For production you should:
- Move secrets to environment variables
- Set `DEBUG=False`
- Define `ALLOWED_HOSTS`
- Configure proper static/media serving and HTTPS

Example (Linux/macOS shell):
```
export DJANGO_SECRET_KEY="your-prod-secret"
export DJANGO_DEBUG="False"
```
Then modify settings to read from `os.environ` (not yet implemented here).

## Database Migrations Workflow
- Modify or create models in `bd2ap1/models.py` (or appropriate app)
- Make migrations: `python manage.py makemigrations`
- Apply: `python manage.py migrate`

## Common Management Commands
```
python manage.py shell          # Open Django shell
python manage.py showmigrations  # See applied/pending migrations
python manage.py check           # Basic project diagnostics
```

## Troubleshooting
| Issue | Possible Fix |
|-------|--------------|
| psycopg2 errors | Ensure PostgreSQL is running & credentials match settings |
| Migration dependency errors | Delete stray migration files and re-run makemigrations (only if safe) |
| "relation does not exist" | You forgot `python manage.py migrate` |
| Static files not loading | Collect static in production: `python manage.py collectstatic` |

## Next Steps / Improvements (Suggestions)
- Add `.env` support (python-dotenv or django-environ)
- Create CRUD views & templates for each domain entity
- Implement validation on ticket sales (seat availability)
- Add API layer (Django REST Framework) for integrations
- Add pagination & filtering for film/session listings
- Write unit tests for business rules (e.g., seat uniqueness, ranking bounds)

## License
Specify a license (e.g., MIT) here if distributing publicly.

---
Happy building! Let this README be your quick reference to extend and maintain the cinema management platform.


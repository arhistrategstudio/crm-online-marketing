# Produkciona priprema (PostgreSQL, Docker, migracije)

## Baza podataka

Razvoj koristi lokalni SQLite fajl (`backend/crm.db`) podrazumevano. Za produkciju je pripremljen PostgreSQL preko `docker-compose.yml`.

```
docker compose up -d database
```

Ovo pokreće Postgres kontejner sa podacima iz `.env` (`POSTGRES_PASSWORD`). Podesi `DATABASE_URL` u `backend/.env` da pokazuje na tu bazu, npr:

```
DATABASE_URL=postgresql+psycopg://crm_user:<POSTGRES_PASSWORD>@localhost:5432/crm_online_marketing
```

## Migracije (Alembic)

Šema baze se u produkciji upravlja preko [Alembic](https://alembic.sqlalchemy.org/) migracija u `backend/alembic/`. Lokalni razvoj i dalje može da se osloni na automatsko kreiranje tabela (`Base.metadata.create_all`, pokreće se pri startu aplikacije) — to je bezopasno i uz Alembic jer samo kreira tabele koje ne postoje.

Primena migracija na produkcionu bazu:

```
cd backend
alembic upgrade head
```

Kreiranje nove migracije posle izmene modela (`app/models/crm.py`):

```
cd backend
alembic revision --autogenerate -m "opis izmene"
```

Uvek pregledaj generisanu migraciju u `backend/alembic/versions/` pre primene — autogenerate ne hvata sve slučajeve (npr. preimenovanje kolone vidi kao brisanje + dodavanje).

## Pokretanje backend-a u kontejneru

```
docker compose up -d --build
```

Ovo pokreće i bazu i backend (`backend/Dockerfile`), koji pri startu automatski izvrši `alembic upgrade head` pa tek onda pokrene `uvicorn` (bez `--reload`, na `0.0.0.0:8000`).

## Frontend u produkciji

Frontend je statička SPA aplikacija (Vite build):

```
cd frontend
npm run build
```

Rezultat (`frontend/dist/`) se postavlja na bilo koji statički hosting (Vercel, Netlify, Nginx, itd.), uz promenljivu `VITE_API_URL` podešenu na adresu produkcionog backend-a pre build-a.

## Promenljive okruženja za produkciju

| Promenljiva | Gde | Opis |
|---|---|---|
| `SECRET_KEY` | backend | Dugačka nasumična vrednost za potpisivanje JWT tokena — obavezno promeniti u produkciji. |
| `DATABASE_URL` | backend | Konekcija na PostgreSQL. |
| `GOOGLE_CLIENT_ID` | backend | Za verifikaciju Google prijave (vidi `docs/auth.md`). |
| `CORS_ORIGINS` | backend | Lista domena frontend-a odvojena zarezom. |
| `VITE_API_URL` | frontend (build-time) | Adresa produkcionog backend API-ja. |
| `VITE_GOOGLE_CLIENT_ID` | frontend (build-time) | Isti Client ID kao backend. |

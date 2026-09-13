# Produkciona priprema (PostgreSQL, Docker, migracije)

## Besplatan hosting (Neon + Render + Vercel)

Preporučena kombinacija za beta verziju — sve tri usluge imaju trajno besplatan plan dovoljan za manji CRM. Naloge na sva tri servisa mora napraviti korisnik lično (prijava preko GitHub naloga, 1-2 minuta po servisu); dalje podešavanje (env promenljive, root direktorijum, build komande) može uraditi agent.

### 1. Baza — [Neon](https://neon.tech) (PostgreSQL)

1. Prijavi se na neon.tech preko GitHub naloga.
2. Napravi novi projekat, npr. `crm-online-marketing`.
3. Iz **Connection Details** kopiraj connection string (oblika `postgresql://user:password@host/dbname?sslmode=require`).
4. Zameni `postgresql://` sa `postgresql+psycopg://` na početku (SQLAlchemy driver koji projekat koristi) — rezultat je vrednost za `DATABASE_URL`.

### 2. Backend — [Render](https://render.com)

1. Prijavi se na render.com preko GitHub naloga i odobri pristup repozitorijumu `crm-online-marketing`.
2. **New + → Blueprint** i izaberi repozitorijum — Render će pronaći `render.yaml` u korenu repoa i sam predložiti web servis (`runtime: docker`, `backend/Dockerfile`, plan `free`).
   - Ako se Blueprint ne ponudi: **New + → Web Service**, izaberi repo, **Root Directory** = `backend`, **Runtime** = Docker, plan **Free**.
3. Popuni environment promenljive u Render panelu (vidi tabelu ispod) — bar `DATABASE_URL` (iz Neon-a) i `SECRET_KEY` (Render može sam generisati nasumičnu vrednost).
4. Posle prvog uspešnog deploy-a, zapamti javnu adresu (oblika `https://crm-online-marketing-backend.onrender.com`) — to je backend API URL. Zdravlje servisa: `<ta-adresa>/api/v1/health`.
5. Besplatan plan „uspava" servis posle ~15 minuta neaktivnosti — prvi sledeći zahtev ga budi za oko 30-50 sekundi. Ovo je prihvatljivo za beta/demo upotrebu, ne za produkciju sa stvarnim klijentima koji očekuju trenutan odgovor.

### 3. Frontend — [Vercel](https://vercel.com)

1. Prijavi se na vercel.com preko GitHub naloga.
2. **Add New → Project**, izaberi repo `crm-online-marketing`.
3. **Root Directory** = `frontend` (Vercel prepoznaje Vite podešavanja automatski — build komanda `npm run build`, izlazni direktorijum `dist`).
4. Dodaj environment promenljivu `VITE_API_URL` = `<Render backend adresa>/api/v1` (npr. `https://crm-online-marketing-backend.onrender.com/api/v1`) pre prvog deploy-a — Vite promenljive se ugrađuju u build, pa izmena posle deploy-a zahteva novi build (Vercel to radi automatski na svaki push, ili ručno „Redeploy").
5. Posle deploy-a, Vercel daje javnu adresu (oblika `https://crm-online-marketing.vercel.app`) — to je live link aplikacije.
6. Vrati se u Render i dodaj tu Vercel adresu u `CORS_ORIGINS` promenljivu backend-a (inače će pregledač blokirati pozive sa frontend-a ka backend-u).

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

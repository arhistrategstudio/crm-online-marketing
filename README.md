# CRM Online Marketing

CRM za marketing agencije i vlasnike biznisa koji prikupljaju upite sa **Facebooka, Instagrama, Vibera i email-a**, prate ih kroz prodajni levak i mere efikasnost reklamnih kampanja.

🔗 **Live aplikacija**: [crm-online-marketing.vercel.app](https://crm-online-marketing.vercel.app) · Backend API: [crm-online-marketing-backend.onrender.com](https://crm-online-marketing-backend.onrender.com/api/v1/health)

## Status projekta — Beta v1

Sve funkcionalnosti ispod rade nad **stvarnim podacima iz baze** (nema tvrdo upisanih/demo prikaza u interfejsu) i pokrivene su automatskim testovima (61 backend test). Ono što namerno **nije** uključeno u ovu verziju je jasno označeno.

| Ekran / funkcija | Stanje |
|---|---|
| Dashboard (KPI, kalendar sastanaka, pretraga, obaveštenja) | ✅ Gotovo |
| Inbox (lista razgovora, poruke po kanalu) | ✅ Gotovo |
| Kontakti (pretraga, dodavanje, sprečavanje duplikata) | ✅ Gotovo |
| Prodajni levak (kanban po fazama) | ✅ Gotovo |
| Kampanje (CRUD, KPI po kampanji) | ✅ Gotovo |
| Podešavanja (profil, promena lozinke) | ✅ Gotovo |
| Prijava — email/lozinka | ✅ Gotovo |
| Prijava — Google | ⚙️ Radi lokalno; na live sajtu čeka da se doda `https://crm-online-marketing.vercel.app` u Authorized JavaScript origins za OAuth Client (Google Cloud Console) |
| Meta (Facebook/Instagram) Lead Ads webhook | ⚙️ Kod gotov i testiran, **namerno diskonektovan** — čeka ispravan Page Access Token (vidi `docs/integrations.md`) |
| Viber Bot API | ⚙️ Kod gotov i testiran, **namerno diskonektovan** — čeka da korisnik lično poveže Viber Public Account (vidi `docs/integrations.md`) |
| Produkcioni hosting (javno dostupan URL) | ✅ Live na Neon + Render + Vercel (besplatan plan — backend se uspava posle ~15 min neaktivnosti, prvi sledeći zahtev čeka 30-50s) |

## Funkcionalnosti

- **Dashboard** — pregled novih upita, aktivnih leadova, poslatih ponuda i efikasnosti kampanja (cena po leadu, broj aktivnih kampanja), pravi kalendar predstojećih sastanaka, pretraga kontakata i obaveštenja u zaglavlju.
- **Inbox** — lista svih razgovora po kanalu (Facebook, Instagram, Viber, Email) sa pregledom poslednje poruke i brojem nepročitanih, i thread za slanje/prijem poruka.
- **Kontakti** — evidencija kontakata sa pretragom (na serveru) i sprečavanjem duplikata (telefon/email/spoljni ID).
- **Prodajni levak** — kanban prikaz leadova po fazama, od upita do naplate, sa promenom faze jednim klikom.
- **Kampanje** — praćenje reklamnih kampanja po kanalu, sa automatskim povezivanjem leadova i KPI (cena po leadu, procenat konverzije).
- **Integracije** — status povezanosti Facebook/Instagram/Viber/Email kanala; Meta Lead Ads i Viber imaju gotov backend kod (vidi tabelu iznad i `docs/integrations.md`).
- **Nalog i prijava** — registracija i prijava email-om/lozinkom ili Google nalogom (Google Identity Services), promena lozinke u Podešavanjima.
- Svetla estetika (Plus Jakarta Sans, gradient pozadina), komandna paleta (`Ctrl/Cmd + K`).

## Tehnologije

- **Frontend**: React 19, TypeScript, Vite.
- **Backend**: FastAPI, SQLAlchemy 2, Pydantic v2, JWT (`PyJWT`), `bcrypt`, `google-auth`.
- **Baza**: SQLite (razvoj), PostgreSQL (produkcija) preko Alembic migracija.

## Pokretanje (razvoj)

### Preduslovi

- Python 3.12+
- Node.js 20+

### Backend

```
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows; na Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # podesi po potrebi (vidi tabelu ispod)
python -m app.seed            # demo podaci + demo nalog (demo@crm.rs / demo1234)
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend je dostupan na `http://127.0.0.1:8000`, dokumentacija API-ja na `http://127.0.0.1:8000/docs`.

### Frontend

```
cd frontend
npm install
cp .env.example .env          # podesi po potrebi
npm run dev
```

Frontend je dostupan na `http://127.0.0.1:5173`. Prijavi se sa demo nalogom (`demo@crm.rs` / `demo1234`) ili napravi novi nalog.

### Testovi

```
cd backend
pytest -v
```

```
cd frontend
npm run build      # TypeScript provera + produkcioni build
```

## Promenljive okruženja

| Promenljiva | Fajl | Opis |
|---|---|---|
| `DATABASE_URL` | `backend/.env` | Konekcija na bazu (podrazumevano lokalni SQLite). |
| `SECRET_KEY` | `backend/.env` | Ključ za potpisivanje JWT tokena — **promeni u produkciji**. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `backend/.env` | Trajanje sesije (podrazumevano 7 dana). |
| `GOOGLE_CLIENT_ID` | `backend/.env` | Za verifikaciju Google prijave — uputstvo u `docs/auth.md`. |
| `CORS_ORIGINS` | `backend/.env` | Dozvoljeni frontend domeni, odvojeni zarezom. |
| `VITE_API_URL` | `frontend/.env` | Adresa backend API-ja. |
| `VITE_GOOGLE_CLIENT_ID` | `frontend/.env` | Isti Google Client ID kao backend. |

## Produkcija

Dve opcije, obe detaljno opisane u [`docs/deployment.md`](docs/deployment.md):

- **Besplatan hosting (Neon + Render + Vercel)** — preporučeno za beta verziju, live URL za par minuta po servisu. Repo sadrži `render.yaml` koji Render prepoznaje automatski.
- **Sopstveni server (Docker)** — `docker compose up -d --build` pokreće PostgreSQL i backend kontejner (koji automatski primenjuje Alembic migracije pre starta).

## Struktura projekta

```
backend/
  app/
    api/        - FastAPI rute (auth, contacts, conversations, leads, campaigns, integrations, meetings, dashboard, webhooks)
    services/   - integracije sa spoljnim API-jima (Meta Graph API, Viber Bot API)
    models/     - SQLAlchemy modeli
    schemas/    - Pydantic šeme
    config.py   - podešavanja iz environment promenljivih
    security.py - heširanje lozinke, JWT, auth dependency
    seed.py     - demo podaci za razvoj
  alembic/      - migracije baze
  tests/        - pytest testovi (61 test)
frontend/
  src/
    components/ - Shell, modali, komandna paleta
    lib/        - API klijent, auth kontekst
    pages/      - Dashboard, Inbox, Kontakti, Prodajni levak, Kampanje, Integracije, Podešavanja, Login, Signup
    types/      - deljeni TypeScript tipovi
docs/           - arhitektura, API, integracije, auth, produkcija
```

## Dokumentacija

- [`docs/architecture.md`](docs/architecture.md) — arhitektura i modul kampanja
- [`docs/api.md`](docs/api.md) — pregled API ruta
- [`docs/auth.md`](docs/auth.md) — prijava, nalozi, podešavanje Google prijave
- [`docs/integrations.md`](docs/integrations.md) — status kanala
- [`docs/deployment.md`](docs/deployment.md) — PostgreSQL, Docker, Alembic

## Doprinošenje

Vidi [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licenca

[MIT](LICENSE)

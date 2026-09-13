# Prijava i nalozi

Aplikacija zahteva prijavu za sve rute osim `/api/v1/health` i `/api/v1/auth/*`. Token je JWT (`HS256`), poslat u `Authorization: Bearer <token>` header-u, i čuva se na frontend-u u `localStorage`.

## Rute

- `POST /api/v1/auth/signup` — `{ name, email, password }` → nalog + token.
- `POST /api/v1/auth/login` — `{ email, password }` → token.
- `POST /api/v1/auth/google` — `{ id_token }` (Google ID token dobijen preko Google Identity Services dugmeta na frontend-u) → token; nalog se automatski kreira ako ne postoji.
- `GET /api/v1/auth/me` — podaci o ulogovanom korisniku.
- `PUT /api/v1/auth/change-password` — `{ current_password?, new_password }`. `current_password` je obavezan samo ako nalog već ima lozinku (lokalni nalog); Google-only nalog može prvi put postaviti lozinku bez tog polja.

Lozinke se heširaju sa `bcrypt` (fallback na `pbkdf2_hmac` ako `bcrypt` paket nije dostupan na ciljnoj platformi).

## Podešavanje Google prijave

1. Idi na [Google Cloud Console](https://console.cloud.google.com/) → napravi projekat (ili koristi postojeći).
2. **APIs & Services → Credentials → Create Credentials → OAuth client ID**.
3. Tip aplikacije: **Web application**.
4. Pod **Authorized JavaScript origins** dodaj `http://127.0.0.1:5173` i `http://localhost:5173` (u produkciji dodaj i pravi domen).
5. Kopiraj generisani **Client ID** (oblika `xxxxxxxxxxxx.apps.googleusercontent.com`). Client Secret nije potreban — backend samo verifikuje ID token.
6. Upiši Client ID na dva mesta:
   - `backend/.env` → `GOOGLE_CLIENT_ID=...`
   - `frontend/.env` → `VITE_GOOGLE_CLIENT_ID=...`
7. Restartuj backend i frontend dev servere. Dugme „Nastavi sa Google nalogom" će se pojaviti na ekranima za prijavu/registraciju čim je `VITE_GOOGLE_CLIENT_ID` postavljen.

## Demo nalog

Skripta `python -m app.seed` kreira demo nalog `demo@crm.rs` / `demo1234` za lokalno testiranje. Ovo nije produkcioni nalog — koristi se samo u razvojnom okruženju.

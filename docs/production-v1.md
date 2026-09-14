# Production v1.0 — aktivacija za prvog klijenta-korisnika

Ovaj dokument opisuje korake kojima se instalacija CRM-a (repo `arhistrategstudio/crm-online-marketing`, live na https://crm-online-marketing.vercel.app) iz test moda prebacuje u **production-ready verziju 1.0** i aktivira za prvog klijenta-korisnika.

Aplikacija je jednokorisnički (tenant) sistem: **prvi registrovan nalog automatski postaje „Vlasnik"** (uloga se čuva na `User.role`). Sve funkcije su omogućene; „test mod" je bio samo vizuelni (demo baneri i poruke o simulaciji) — uklonjen je u koraku 111. Integracije (Meta Webhook, Viber) se stvarno aktiviraju unošenjem tokena u okruženje backend servisa.

## 0. Preduslovi (jednom po klijentu)

1. Deploy bazira na **Render** (backend + PostgreSQL/Neon) i **Vercel** (frontend) — vidi `docs/deployment.md` i `render.yaml`.
2. Pri prvom deploy-u Render pokreće `alembic upgrade head` (u `backend/Dockerfile`) — migracije se primenjuju automatski.
3. U Render Dashboard-u za backend servis podesi sledeće env promenljive (sve osim `SECRET_KEY` i baze su opcione sve dok ih klijent ne koristi):

| Promenljiva | Vrsta | Šta omogućava |
|---|---|---|
| `DATABASE_URL` | obavezno | Neon/PostgreSQL konekcija (Render koristi `sync:false`) |
| `SECRET_KEY` | obavezno | JWT potpis — Render automatski generiše |
| `CORS_ORIGINS` | obavezno | npr. `https://crm-online-marketing.vercel.app` |
| `GOOGLE_CLIENT_ID` | opciono | Google prijava (isti ID kao `VITE_GOOGLE_CLIENT_ID` u frontendu) |
| `META_APP_SECRET`, `META_VERIFY_TOKEN`, `META_PAGE_ACCESS_TOKEN` | opciono | Meta Lead Ads webhook + automatsko upisivanje upita |
| `VIBER_AUTH_TOKEN` | opciono | Viber Public Account webhook i slanje odgovora |

## 1. Kreiranje naloga prvog klijenta

1. Otvoriti live aplikaciju → „Napravi nalog".
2. Registrovan prvi nalog dobija ulogu **Vlasnik**. Svaki sledeći nalog je običan **Korisnik** (safe: provera se radi po broju postojećih korisnika — `app/api/auth.py: _first_user_role`).
3. Preporučeni prvi korak nakon prijave: **Promeni lozinku** (Podešavanja) i opciono poveži Google prijavu (isti email).

## 2. Aktivacioni checklist (vidi i u aplikaciji → Dashboard → „Aktivacija aplikacije")

Aplikacija na Dashboard-u prikazuje korake preko `GET /api/v1/dashboard/setup` (`SetupStatus`); karton nestaje kad su svi gotovi.

| Ključ | Korak | Kada je gotovo |
|---|---|---|
| `account` | Kreiran vlasnički nalog | postoji bar jedan korisnik |
| `google` | Google prijava podešena | `GOOGLE_CLIENT_ID` postavljen na serveru |
| `channels` | Povezani kanali (Meta/Viber) | bar jedan kanal u bazi ima status `Povezano` |
| `contacts` | Dodati prvi kontakti | bar jedan kontakt u bazi |
| `campaigns` | Kreirana prva kampanja | bar jedna kampanja u bazi |
| `leads` | Prvi upiti u levku | bar jedan lead u bazi |

## 3. Stvarno povezivanje kanala (Meta i Viber)

Status u UI-ju (Integracije) je prikaz stanja u bazi (`/integrations`). Prava konekcija se uspostavlja kroz token u env okruženju:

### Meta Lead Ads
1. Kroz **Meta for Developers** → aplikacija → „Autopost" (Business Verification već urađena).
2. Generisati **Page Access Token** za stranicu klijenta („VizantNeimar.rs") sa dozvolom `leads_retrieval` (videti `Progress.md` korak 95 — token mora biti Page, ne User token).
3. Upisati `META_PAGE_ACCESS_TOKEN`, `META_APP_SECRET`, `META_VERIFY_TOKEN` u Render env i redeploy-ovati.
4. U Meta aplikaciji podesiti webhook na `https://<backend-url>/api/v1/webhooks/meta` sa istim verify tokenom (`app/api/webhooks.py` proverava potpis kada je `META_APP_SECRET` postavljen).
5. Test: Ads Manager → „Test Lead" → potvrditi novi Contact+Lead u CRM-u.

### Viber
1. Prijaviti se na `partners.viber.com` (telefon + OTP), napraviti/potražiti Public Account, dobiti **Auth Token**.
2. Upisati `VIBER_AUTH_TOKEN` u Render env i redeploy-ovati.
3. Jednokratno pozvati `set_webhook()` prema `https://<backend-url>/api/v1/webhooks/viber` (detalji u `docs/integrations.md`).

Kanali koji nemaju token ostaju „Nije povezano" — UI to prikazuje bez lažne simulacije (korak 111).

## 4. Priprema podataka

- Podrazumevani demo nalog `demo@crm.rs`/`demo1234` (u `app/seed.py`) se **ne pokreće automatski** u produkciji — `seed` se izvršava samo ručno (`python -m app.seed`). Za prvog klijenta poželjno je, ako demo podaci postoje, napraviti novu bazu ili očistiti demo redove pre aktivacije.
- Dodati prve kontakte, kampanju i upite kroz UI (levak podržava 9 faza, izvore, vlasnike i podsetnike).

## 5. Verifikacija produkcije

1. `GET https://<backend-url>/api/v1/version` → `{"version": "1.0.0"}`.
2. `GET https://<backend-url>/api/v1/health` → `{"status": "ok"}`.
3. Prijava preko mejl/lozinke i (opciono) Google.
4. Dashboard `setup` vraća sve korake gotove (`configured: true`).
5. Render log: `alembic upgrade head` prolazi bez grešaka (migracija `c3d4e5f6a7b8` dodatno širi levak/ponude).

## 6. Izlazak iz „test moda" što je sve urađeno (korak 111)

- [x] Uklonjeni demo baneri (Dashboard, Integrations) i poruke o „simulaciji" integracija.
- [x] Prvi korisnik dobija ulogu „Vlasnik" (`signup` i Google prijava).
- [x] `GET /api/v1/dashboard/setup` — aktivacioni checklist za prvog klijenta.
- [x] Verzija aplikacije **1.0.0** (frontend `package.json`, backend `FastAPI.version`, `/api/v1/version`, `v1.0` badge u sidebaru).
- [x] Zamenjen hardkodovani engleski podnaslov u topbaru srpskim opisima strana.
- [x] Obrisani mrtvi CSS fajlovi (`auth.css`, `contact-modal.css`, `contact-toolbar.css`) i `.demo` alias.
- [ ] Dizajn UI prema Figma-specifikaciji — **u toku/na čekanju** dok korisnik ne dostavi eksport ekrana (Figma zahteva prijavu, videti `Progress.md` korak 110).
# Progress CRM Online Marketing

Ovaj fajl je dnevnik rada na projektu. Posle svakog završenog koraka dopunjuje se najnovijim stanjem.

## Završeno

1. Napravljena je struktura projekta: `frontend`, `backend` i `docs`.
2. Postavljen je React/Vite frontend sa modernim SaaS izgledom, svetlom/tamnom temom, akcentnim bojama i bočnom navigacijom.
3. Napravljeni su početni ekrani: Dashboard, Inbox, Kontakti, Prodajni levak, Integracije i Podešavanja.
4. Dodata je komandna paleta za navigaciju (`Ctrl/Cmd + K`).
5. Kontakti se učitavaju i čuvaju preko FastAPI backend-a; postoji obrazac za dodavanje kontakta.
6. Postavljeni su modeli podataka i API rute za kontakte, leadove i Dashboard pokazatelje.
7. Backend koristi lokalnu SQLite bazu za razvoj (`backend/crm.db`); PostgreSQL Docker konfiguracija je pripremljena za kasnije.
8. Backend je pokrenut na `http://127.0.0.1:8000`, frontend na `http://127.0.0.1:5173`.
9. Provere: frontend build prolazi; backend zdravstveni test prolazi.

10. Uređen je Inbox obrazac: dugme „Pošalji“ ima primarni stil i pravilan razmak od polja poruke.
11. U Prodajnom levku je dodat pravilan razmak između padajućeg menija i oznake trenutne faze.
12. Dugmad „Podesi“ na Integracijama su stilizovana kao jasne primarne akcije.

## Trenutni korak

13. Provera izmene interfejsa je uspešno završena.
14. Dashboard je povezan sa backend API rutom za pokazatelje.
15. Pripremljena je skripta za kontrolisane demo podatke: kontakti, razgovori, poruke i leadovi.
16. Demo podaci su učitani u lokalnu razvojnu bazu: 10 kontakata, 10 razgovora, 25 poruka i 4 leada.
17. Padajući meni Prodajnog levka povezan je sa backend API-jem za promenu faze.
18. Dodate su backend API rute za Inbox razgovore i poruke.
19. Inbox ekran je povezan sa API-jem za učitavanje i slanje poruka.
20. Dodate su backend API rute za status integracija.
21. Ekran Integracije je povezan sa backend API-jem: učitava stvarni status kanala (Facebook, Instagram, Viber, Email) i dugme „Podesi“/„Isključi“ menja status preko `PUT /integrations/{channel}`. Dodata je i `.danger` CSS klasa za status „Greška“.
22. Backend proces je bio zastareo (pokrenut pre dodavanja integrations rute) i restartovan je; ubuduće po potrebi restartovati posle promena u `app/main.py` ili API rutama jer server ne radi sa `--reload`.
23. Prošireni su automatski testovi: dodat je `backend/tests/conftest.py` sa izolovanom in-memory SQLite bazom (preko `dependency_overrides` za `get_db`, bez pokretanja app lifespan-a, pa se prava razvoja baza `crm.db` ne dira). Dodati su `test_contacts.py` (kreiranje, provera dupliranih kontakata po telefonu/email-u/external_id-u, pretraga, get/update i 404 slučajevi) i `test_leads.py` (kreiranje leada, provera nepostojećeg kontakta, duplirani lead za isti kontakt, listanje i ažuriranje faze/vrednosti, uključujući da delimično ažuriranje bez polja `value` ne briše postojeću vrednost). Svih 18 testova prolazi (`.venv/Scripts/python.exe -m pytest tests/ -v`).

24. Backend server je restartovan sa `--reload` opcijom (`uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`); uklonjeni su i stari duplirani procesi (bila su pokrenuta dva uvicorn procesa istovremeno). Ubuduće se izmene u `app/` automatski učitavaju bez ručnog restarta.
25. Dodata je autentifikacija: `User` model proširen (`password_hash`, `google_id`, `auth_provider`), heširanje lozinke (`bcrypt` sa `pbkdf2` fallback-om), JWT tokeni (`PyJWT`), i rute `/api/v1/auth/signup|login|google|me|change-password`. Sve postojeće API rute (kontakti, razgovori, leadovi, integracije, dashboard) i nove rute za kampanje sada zahtevaju prijavu (`Authorization: Bearer <token>`), osim `/health` i `/auth/*`.
26. Dodat je modul „Kampanje": `Campaign`/`CampaignStatus` model, `Lead.campaign_id` veza, CRUD rute `/api/v1/campaigns` sa izračunatim KPI poljima (broj leadova, cena po leadu, procenat konverzije), i dashboard KPI (`campaigns_active`, `avg_cost_per_lead`).
27. Prošireni su testovi: `conftest.py` sada ima `client` (auto-prijavljen) i `anon_client` fixture; dodati `test_auth.py` i `test_campaigns.py`. Svih 38 testova prolazi.
28. Pripremljena je PostgreSQL produkciona putanja: `app/config.py` (pydantic-settings), Alembic (`backend/alembic/`, početna migracija `0feced89c75d_initial_schema.py` generisana i proverena da se čisto primenjuje), `backend/Dockerfile` (pokreće `alembic upgrade head` pa `uvicorn`), prošireni `docker-compose.yml` sa `backend` servisom. Docker Desktop nije bio dostupan u ovom okruženju za direktnu proveru protiv pravog Postgres kontejnera — migracija je proverena protiv privremene prazne SQLite baze (Alembic generiše dijalekt-nezavisne komande, pa je primenljiva i na Postgres); preporučuje se provera protiv stvarnog Postgres-a kad Docker bude dostupan.
29. Frontend `main.tsx` (54 guste linije) rastavljen je na module: `lib/api.ts`, `lib/auth.tsx` (React auth kontekst), `types/index.ts`, `components/` (Shell, CommandPalette, ContactModal, CampaignModal, GoogleButton), `pages/` (Login, Signup, Dashboard, Inbox, Kontakti, Prodajni levak, Kampanje, Integracije, Podešavanja). Dodate su Login/Signup stranice sa Google prijavom (Google Identity Services, aktivira se kad je `VITE_GOOGLE_CLIENT_ID` podešen), a Podešavanja imaju karticu za promenu/postavljanje lozinke. `frontend/index.html` je ispravljen (nedostajali su `<!doctype>/<html>/<head>/<body>`).
30. Google OAuth: korisnik je napravio Google Cloud projekat i Web application OAuth Client ID; čeka se da vrednost bude prosleđena da se upiše u `backend/.env` i `frontend/.env` (polja su pripremljena, prazna).
31. Vizuelna provera u pregledaču (Claude in Chrome) nije mogla da se izvrši u ovoj sesiji — alat je dosledno vraćao grešku „Script injection timed out" čak i na `example.com`, što ukazuje na privremeni problem sa ekstenzijom, ne sa aplikacijom. Backend je u potpunosti proveren preko `curl` (signup/login/me/change-password/campaigns/dashboard) i pytest-a; frontend `npm run build` prolazi bez grešaka. Ručna provera u pravom pregledaču je preporučena kad se browser alat oporavi.
32. Pripremljena je GitHub struktura: `LICENSE` (MIT), `.editorconfig`, `.github/workflows/ci.yml` (backend pytest + frontend build), `CONTRIBUTING.md`, prošireni `docs/` (novi `auth.md`, `deployment.md`, ažurirani `architecture.md`/`integrations.md`/`api.md`), pun `README.md`, i `.gitignore` dopunjen sa `*.db`/`*.tsbuildinfo`.

## Sledeće

33. Kad korisnik prosledi Google OAuth Client ID, upisati ga u `backend/.env` i `frontend/.env` i ručno testirati Google prijavu.
34. Ponoviti vizuelnu proveru u pregledaču (Claude in Chrome) kada se alat oporavi, ili zamoliti korisnika da ručno prođe kroz signup/login/Kampanje/promenu lozinke na `http://127.0.0.1:5173`.
35. Kada Docker Desktop bude dostupan, pokrenuti `docker compose up -d database`, primeniti `alembic upgrade head` i potvrditi da backend radi protiv pravog PostgreSQL-a.

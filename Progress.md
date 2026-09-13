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

33. Projekat je postavljen na GitHub: `git init`, prvi commit i push preko `gh repo create` na **https://github.com/arhistrategstudio/crm-online-marketing** (javan repo, MIT licenca). `.github/workflows/ci.yml` NIJE pushovan — GitHub CLI token nema `workflow` OAuth scope pa je GitHub odbio taj fajl; fajl ostaje lokalno i biće dodat naknadno (vidi Sledeće).
34. Korisnik je ručno testirao aplikaciju u pravom pregledaču (Claude in Chrome alat je ostao neupotrebljiv i posle više pokušaja i buđenja Chrome prozora — verovatno trajna posledica ranijeg kritičnog nedostatka RAM memorije u ovoj sesiji). Pronađena i ispravljena greška: u Podešavanjima, promena lozinke je bacala `Cannot read properties of null (reading 'reset')` — `event.currentTarget` u `frontend/src/pages/Settings.tsx` postaje `null` posle `await` (React nulira SyntheticEvent posle sinhronog dela handler-a), pa je forma referenca sada uzeta pre `await` poziva. Ostale forme (Login, Signup, Contacts, Campaigns) nisu imale ovaj problem jer ne koriste `event.currentTarget` posle `await`. **Ova ispravka još nije komitovana/pushovana na GitHub.**

35. Ispravka u `frontend/src/pages/Settings.tsx` (promena lozinke) je komitovana (`7a172b0`) i pushovana na GitHub.
36. Korisnik je odobrio `workflow` scope GitHub CLI tokenu preko device flow-a (`gh auth refresh -h github.com -s workflow`). `.github/workflows/ci.yml` je komitovan (`d910b93`) i pushovan. Prvi CI run je pao: backend job je koristio `pytest -v` (konzolna skripta), koja za razliku od `python -m pytest` ne dodaje tekući direktorijum u `sys.path`, pa `app` paket nije mogao da se importuje (`ModuleNotFoundError: No module named 'app'`). Ispravljeno na `python -m pytest -v` (`d703e43`) i pushovano — CI sada prolazi (i backend i frontend job).

37. Claude in Chrome je ponovo probao (nova kartica, nova grupa kartica) da automatizovano testira ekrane — greška „Script injection timed out"/„Page still loading" i dalje se javlja iako se stranica vidljivo učitava (naslov taba je ispravan). Potvrđeno da je ovo i dalje trajni problem sa ekstenzijom (isto kao korak 31), ne sa aplikacijom.
38. Otkriven je uzrok: sistem je bio kritično pri kraju sa RAM memorijom (0.38 GB slobodno od 15.64 GB), pa je harness ugasio pozadinske dev servere (backend uvicorn i frontend `npm run dev`) — to je verovatno i pravi uzrok trajnih problema sa Claude in Chrome ekstenzijom. Najveći potrošač je bio `vmmemWSL` (WSL2 VM koji koristi Docker Desktop). Na zahtev korisnika ugašeni su nepotrebni pozadinski programi (Discord, ChatGPT desktop app, WhatsApp) čime je oslobođeno ~1.3 GB; Excel/Word/Notepad su namerno preskočeni jer su imali nesačuvane/AutoRecovered dokumente otvorene. Backend i frontend dev serveri su ponovo pokrenuti i potvrđeno rade (`/api/v1/health` → `{"status":"ok"}`, frontend → HTTP 200).
39. Docker Desktop je pokrenut od strane korisnika. Izvršeno je `docker compose up -d database` — kontejner `crm-online-marketing-db` (Postgres 16-alpine) je pokrenut i zdrav (`healthy`). Primenjena je `alembic upgrade head` protiv pravog PostgreSQL-a (`postgresql+psycopg://crm_user:...@localhost:5432/crm_online_marketing`, lozinka iz root `.env`) — migracija je čisto prošla i kreirala svih 8 tabela (`alembic_version`, `campaigns`, `contacts`, `conversations`, `integrations`, `leads`, `messages`, `users`). Radi potvrde da backend zaista radi protiv Postgres-a, pokrenuta je privremena druga instanca backend-a na portu 8001 (sa `DATABASE_URL` prebačenim na Postgres, bez diranja glavnog dev servera na portu 8000 koji i dalje koristi SQLite) i uspešno testirani `/health`, `/auth/signup` i `/auth/login` — testni korisnik je posle toga obrisan iz baze, a privremena instanca ugašena. Lokalni dev i dalje podrazumevano koristi SQLite (`backend/.env` nije menjan); prelazak na trajno korišćenje Postgres-a za dev je opciona sledeća odluka.

## Sledeće

40. Kad korisnik prosledi Google OAuth Client ID, upisati ga u `backend/.env` i `frontend/.env` i ručno testirati Google prijavu. (Za sada preskočeno na zahtev korisnika.)
41. Nastaviti ručno testiranje ostalih ekrana (Dashboard, Inbox, Kontakti, Prodajni levak, Kampanje, Integracije) na `http://127.0.0.1:5173` — korisnik testira ručno i prijavljuje nove greške, pošto Claude in Chrome alat ostaje neupotrebljiv (verovatno zbog memorijskog pritiska, vidi korak 38).

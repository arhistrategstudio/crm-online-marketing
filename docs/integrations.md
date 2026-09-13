# Integracije

MVP prikazuje Facebook, Instagram, Viber i Email kao kanale.

Dok se ne unesu stvarni pristupni podaci i ne napravi veza sa servisom, status kanala mora biti **Nije povezano**. Demo poruke su lokalni test podaci i nisu stvarne poruke korisnika.

## Kampanje i kanali

Modul „Kampanje" (`/api/v1/campaigns`) koristi iste kanale (Facebook, Instagram, Viber) da poveže reklamnu kampanju sa leadovima koje je ta kampanja generisala. Ovo je nezavisno od statusa integracije — kampanje se mogu pratiti ručno i pre nego što je stvarna API veza sa Facebook/Instagram/Viber servisom uspostavljena.

## Meta Lead Ads webhook (automatsko prikupljanje leadova)

Prva prava (ne-demo) konekcija sa Meta-om: kad neko popuni Instant Form reklamu na Facebook/Instagram, Meta pozove naš webhook, mi preuzmemo pun sadržaj leada preko Graph API-ja i automatski napravimo Contact + Lead u bazi.

**Endpoints** (javni, bez JWT autentifikacije — Meta ih zove direktno; zaštićeni su `verify_token`-om i HMAC potpisom):
- `GET /api/v1/webhooks/meta` — jednokratna verifikacija pretplate (Meta šalje `hub.mode`, `hub.verify_token`, `hub.challenge`; server mora vratiti `hub.challenge` ako se token poklapa sa `META_VERIFY_TOKEN`).
- `POST /api/v1/webhooks/meta` — obaveštenje o novom leadu (`leadgen_id`); server proverava `X-Hub-Signature-256` potpis (HMAC-SHA256 sa `META_APP_SECRET`), preuzima pune podatke sa `GET https://graph.facebook.com/{verzija}/{leadgen_id}` (koristi `META_PAGE_ACCESS_TOKEN`), i kreira Contact (`source=facebook`, dedup po telefonu/emailu) + Lead (`stage=new_inquiry`). Svaki `leadgen_id` se obrađuje samo jednom (`meta_lead_events` tabela čuva istoriju/audit trag i sprečava duplirano procesiranje pri Meta retry-jevima).

**Šta korisnik treba da pripremi na Meta strani (van koda):**
1. Meta Business Manager nalog + verifikovana Facebook stranica (i Instagram nalog povezan sa njom, ako se žele IG lead reklame).
2. Meta App na [developers.facebook.com](https://developers.facebook.com) sa dodatim „Webhooks" i „Facebook Login for Business" proizvodima.
3. Instant Form (Lead Ads) forma napravljena na stranici.
4. Webhook pretplata u Meta App podešavanjima: URL = `https://<javno-dostupan-domen>/api/v1/webhooks/meta`, Verify Token = ista vrednost kao `META_VERIFY_TOKEN` u `.env`, polje za pretplatu = `leadgen`. **Backend mora biti javno dostupan preko HTTPS-a** (lokalni `127.0.0.1` ne radi za Meta) — za lokalno testiranje potreban je tunel (npr. ngrok/cloudflared) čiji se javni URL upiše kod Meta-e.
5. Dugotrajan Page Access Token sa `leads_retrieval` i `pages_manage_metadata` dozvolama (bez punog `ads_management`) — upisati u `META_PAGE_ACCESS_TOKEN`. Za produkciju, ove dozvole zahtevaju Meta App Review + Business Verification (traje danima/nedeljama).
6. `META_APP_SECRET` (iz Meta App → Settings → Basic) upisati u `.env`.

**Napomena:** pravo kreiranje/pauziranje kampanja, budžet i sinhronizacija potrošnje iz Meta Ads Managera nisu deo ovog koraka — to zahteva pun OAuth login flow (korisnik se prijavljuje svojim Meta nalogom) i `ads_management` dozvolu, planirano za kasnije.

## Viber Bot API (poruke iz Inbox-a)

Za razliku od Meta integracije, Viber je potpuno odvojen sistem (Viber Bot API, REST, autentifikacija preko jednog „Auth Token"-a — nema OAuth-a). Kod postoji i funkcioniše, ali **namerno nije povezan ni na jedan pravi Viber nalog** — `VIBER_AUTH_TOKEN` u `.env` je prazan. Dok je prazan, sve ostaje kao i danas: dolazne poruke se ne primaju, a odlazne poruke iz Inbox-a se samo čuvaju u bazi (ne šalju se stvarno).

**Endpoints** (javna ruta, bez JWT-a — Viber je zove direktno; zaštićena `X-Viber-Content-Signature` HMAC potpisom kad je `VIBER_AUTH_TOKEN` podešen):
- `POST /api/v1/webhooks/viber` — prima sve Viber event tipove. Za `event: "message"` kreira/pronalazi Contact (`source=viber`, dedup po Viber `sender.id`) i Conversation (`channel=viber`), i upisuje dolaznu poruku. Ostali event tipovi (`subscribed`, `conversation_started`, `delivered`, `seen`, Viber-ova sopstvena `webhook` provera pri `set_webhook` pozivu...) se samo potvrde sa 200, bez efekta.
- Slanje odgovora: postojeća ruta `POST /api/v1/conversations/{id}/messages` (koju Inbox ekran već koristi) sada, ako je razgovor `channel=viber` I `VIBER_AUTH_TOKEN` je podešen, pozove `app/services/viber.py:send_message()` da stvarno pošalje poruku nazad korisniku preko Viber-a.

**Šta bi trebalo da se uradi kad korisnik odluči da poveže pravi Viber nalog:**
1. U Viber aplikaciji (telefon), napraviti Public Account/Bot za posao (Podešavanja → Public Accounts/Business).
2. Prijaviti se na [partners.viber.com](https://partners.viber.com) (traži broj telefona + OTP kod koji stiže u samu Viber aplikaciju — ovo mora korisnik lično, agent ne može ovo da uradi umesto njega).
3. Iz Admin panela preuzeti **Auth Token** za taj Public Account i upisati ga u `VIBER_AUTH_TOKEN` u `.env`.
4. Jednokratno pozvati `app/services/viber.py:set_webhook(url, auth_token)` sa javno dostupnim HTTPS URL-om (`https://<domen>/api/v1/webhooks/viber`) — isti zahtev kao kod Meta-e, lokalni `127.0.0.1` ne radi, treba tunel za lokalno testiranje ili pravi hosting za produkciju.
5. Restartovati backend da pokupi novi `VIBER_AUTH_TOKEN` — od tog trenutka dolazne Viber poruke se automatski pojavljuju u Inbox-u, a odgovori iz Inbox-a se stvarno šalju nazad.

**Napomena:** Viber-ov Send Message API dozvoljava slanje poruke korisniku samo pošto je on PRVI napisao botu (isto pravilo kao kod većine chat bot platformi) — ne može se bot koristiti za hladno slanje poruka nepoznatim kontaktima.

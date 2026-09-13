# API

Svi API pozivi počinju sa `/api/v1/`.

`GET /api/v1/health` proverava da li server radi (javna ruta).

Sve ostale rute zahtevaju prijavu (`Authorization: Bearer <token>`) — vidi `docs/auth.md`.

| Grupa | Prefiks | Opis |
|---|---|---|
| Nalog | `/auth` | Registracija, prijava, Google prijava, trenutni korisnik, promena lozinke. |
| Kontakti | `/contacts` | CRUD za kontakte, pretraga (`?search=`), provera duplikata (telefon/email/spoljni ID). |
| Razgovori | `/conversations` | Lista razgovora (sa imenom kontakta i poslednjom porukom), poruke po razgovoru, slanje odgovora. Otvaranje razgovora (`GET /conversations/{id}/messages`) resetuje broj nepročitanih poruka. |
| Prodajni levak | `/leads` | Leadovi sa spojenim podacima o kontaktu (telefon, mejl, izvor, odgovorna osoba, beleška), faze levka (`new_inquiry → contacted → offer_sent → negotiation → waiting_response → deal_won → scheduled → paid → deal_lost`), vrednost, podsetnik (`next_activity`/`next_activity_at`), `followup_due` i broj ponuda. Dodatno: `GET /leads/followups` (poslata ponuda bez odgovora), `GET/POST /leads/{id}/activities` (beleška/poziv/email/aktivnost), `GET/POST /leads/{id}/proposals` (kreiranje ponude prebacuje lead u `offer_sent`, beleži `sent_at` i zakazuje follow-up), `GET /leads/{id}/history` (spojena hronologija poruka, aktivnosti i ponuda). |
| Kampanje | `/campaigns` | CRUD za reklamne kampanje, sa izračunatom cenom po leadu i konverzijom. |
| Integracije | `/integrations` | Status povezanosti kanala (Facebook, Instagram, Viber, Email) — demo status, vidi `docs/integrations.md`. |
| Sastanci | `/meetings` | Kalendar sastanaka (GET sa `start`/`end` filterom, POST, DELETE) — koristi ga Dashboard kalendar. |
| Dashboard | `/dashboard` | `/summary` (KPI + vrednost levka: aktivni leadovi, potencijalna vrednost, zatvoreno ovog meseca, poslate ponude, dobitak/gubitak, procenat zatvorenih, prosečno vreme do prodaje, razlozi gubitka), `/prospects` (najnoviji leadovi sa imenom kontakta), `/notifications` (uživo izračunata obaveštenja — nepročitani razgovori + novi upiti + podsetnici, bez perzistencije). |
| Webhook-ovi (javni) | `/webhooks` | `/webhooks/meta` (Meta Lead Ads) i `/webhooks/viber` (Viber Bot API) — bez JWT-a, pozivaju ih spoljni servisi direktno; zaštićeni potpisom/verify tokenom. Detalji u `docs/integrations.md`. |

Interaktivna dokumentacija (Swagger UI) sa svim poljima i primerima dostupna je na `/docs` dok backend radi (npr. `http://127.0.0.1:8000/docs`).

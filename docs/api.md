# API

Svi API pozivi počinju sa `/api/v1/`.

`GET /api/v1/health` proverava da li server radi (javna ruta).

Sve ostale rute zahtevaju prijavu (`Authorization: Bearer <token>`) — vidi `docs/auth.md`.

| Grupa | Prefiks | Opis |
|---|---|---|
| Nalog | `/auth` | Registracija, prijava, Google prijava, trenutni korisnik, promena lozinke. |
| Kontakti | `/contacts` | CRUD za kontakte, pretraga, provera duplikata. |
| Razgovori | `/conversations` | Inbox razgovori i poruke po kanalu. |
| Prodajni levak | `/leads` | Leadovi, faze levka, vrednost, vezivanje za kampanju. |
| Kampanje | `/campaigns` | CRUD za reklamne kampanje, sa izračunatom cenom po leadu i konverzijom. |
| Integracije | `/integrations` | Status povezanosti kanala (Facebook, Instagram, Viber, Email). |
| Dashboard | `/dashboard` | Agregatni pokazatelji (leadovi, kampanje, cena po leadu). |

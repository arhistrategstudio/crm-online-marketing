# Arhitektura

Projekat ima tri dela:

1. **Frontend** (React + Vite, `frontend/`) prikazuje CRM u pregledaču i poziva API. Nakon prijave prikazuje Dashboard, Inbox, Kontakte, Prodajni levak, Kampanje, Integracije i Podešavanja; pre prijave prikazuje ekrane za prijavu/registraciju.
2. **Backend** (FastAPI + SQLAlchemy, `backend/`) čuva podatke, proverava ih, izdaje JWT tokene i vraća podatke frontendu preko `/api/v1/` adresa. Sve rute osim `/api/v1/auth/*` i `/api/v1/health` zahtevaju prijavu (`Authorization: Bearer <token>`).
3. **Baza podataka** — u razvoju lokalni SQLite fajl (`backend/crm.db`), u produkciji PostgreSQL (vidi `docs/deployment.md`).

Adapteri za Facebook, Instagram, Viber i email (stvarne integracije) prevodiće spoljne poruke u isti format razgovora i poruka. U MVP-u koristimo lokalne demo poruke; nijedan spoljni kanal neće biti lažno prikazan kao povezan (vidi `docs/integrations.md`).

## Modul „Kampanje"

Kampanje predstavljaju reklamne akcije na Facebook/Instagram/Viber kanalima. Svaki lead se opciono vezuje za kampanju (`Lead.campaign_id`) kako bi se merila efikasnost: broj leadova po kampanji, cena po leadu (potrošnja / broj leadova) i procenat konverzije (leadovi u fazi „Zakazano / Plaćeno"). Dashboard prikazuje agregate za sve aktivne/završene kampanje.

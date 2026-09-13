# Doprinošenje projektu

Hvala na interesovanju za CRM Online Marketing! Kratko uputstvo pre nego što pošalješ izmene.

## Grane

- `main` je uvek stabilna grana.
- Novu funkcionalnost ili ispravku radi na zasebnoj grani, npr. `feature/kampanje-filter` ili `fix/inbox-scroll`.

## Pre slanja Pull Request-a

1. Pokreni backend testove:
   ```
   cd backend
   .venv/Scripts/python.exe -m pytest tests/ -v
   ```
2. Proveri da frontend prolazi build/typecheck:
   ```
   cd frontend
   npm run build
   ```
3. Uveri se da GitHub Actions CI (`.github/workflows/ci.yml`) prolazi na tvojoj grani.

## Stil komita

Kratke, jasne poruke u imperativu, npr. `Dodaj filter kampanja po kanalu` umesto `Dodao sam...`. Jedan commit = jedna logička izmena kad god je moguće.

## Pull Request

U opisu PR-a navedi:
- šta je promenjeno i zašto,
- kako je testirano,
- da li menja API ili šemu baze (i da li je potrebna nova Alembic migracija — pogledaj `docs/deployment.md`).

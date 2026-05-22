# Demo 01 - Basic account mapping & renewal alerts

This demo shows PARTNERMAP reading three partnership agreements written as
YAML and computing:

1. **Account overlap** between partners (which customers you both touch),
   matched via hashed/normalized tokens so the raw list never has to be
   shared with the other side.
2. **Renewal alerts** for agreements that are overdue or due soon.

## Files

- `partners.yaml` - a single file containing a `partners:` list with three
  partners (AcmeCloud, DataForge, NimbusCRM), their tiers, renewal dates,
  and account lists. Note the account names use varied casing/suffixes
  (e.g. `Globex, Inc.` vs `globex`) to demonstrate normalization.

## Run it

```bash
# Table view (deterministic 'today' so the demo output is stable)
python -m partnermap analyze demos/01-basic --today 2026-06-08

# JSON for CI / jq
python -m partnermap analyze demos/01-basic --today 2026-06-08 --format json

# Gate CI on overdue renewals only
python -m partnermap analyze demos/01-basic --today 2026-06-08 --fail-on overdue
```

## Expected result

With `--today 2026-06-08`:

- **Overlaps**
  - AcmeCloud <> DataForge share **Globex** (matched across
    `Globex, Inc.` and `globex`) and **Initech**.
  - AcmeCloud <> NimbusCRM share **Initech**.
- **Renewal alerts** (60-day window)
  - `DataForge` renews `2026-05-01` -> **overdue**.
  - `AcmeCloud` renews `2026-07-01` -> **due-soon**.
  - `NimbusCRM` renews `2026-12-01` -> not flagged (outside window).
- Summary: 3 partners, 2 overlap pairs, 2 renewal alerts (1 overdue).

Exit code is `0` for the plain run, and `1` for `--fail-on overdue`
(because DataForge is overdue).

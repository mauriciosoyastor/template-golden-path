# Contributing

Gracias por contribuir a `template-golden-path`.

## Golden Path (obligatorio)

1. **Issue** → label `needs-triage` → `ready-for-agent` (triage)
2. `wayfinder?` si el mapa lo exige
3. `to-tickets` genera `tracer-bullet` con `Blocked by`
4. `gitnexus-plan` (`impact` + `pdg:true` `detect_changes`)
5. `gitnexus-work` + `harness verify` (`verdict:ok risk:low`)
6. `code-review` two-axes (Standards + Spec)
7. Merge humano

No edites sin `impact` previo ni commitees sin `detect_changes`.

## Setup local

```bash
uv sync --all-packages
node .gitnexus/run.cjs analyze --index-only
uv run ruff format . && uv run ruff check --fix . && uv run mypy tu_paquete && uv run pytest -q
uv run python harness/check_context.py
```

## CI

`ci.yml` corre lo mismo con `uv`. `pre-commit` bloquea `ruff+mypy+pytest` en `tu_paquete`.

## Licencia

Al contribuir aceptas que tu aporte se licencie bajo MIT (`LICENSE`).

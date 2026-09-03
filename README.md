# template-golden-path

Template opencode con **Golden Path Fusión** único — listo para `npx degit`.

## Golden Path

```
Issue → triage(needs-triage→ready-for-agent) → wayfinder? → to-tickets(tracer-bullet) → gitnexus-plan(impact+pdg) → gitnexus-work(+harness verify) → code-review(two-axes) → merge humano
```

Single-writer `harness/trajectory.jsonl`, `sandbox-edit` default, `MUST impact before edit / detect_changes before commit`.

## Uso

```bash
npx degit mauriciosoyastor/template-golden-path my-project
cd my-project
uv sync --all-packages
node .gitnexus/run.cjs analyze --index-only  # indexa GitNexus pdg:true
uv run ruff check . && uv run ruff format --check . && uv run mypy tu_paquete && uv run pytest -q
uv run python harness/harness.py --intent "demo"  # verifica harness P-E-V verdict:ok
```

Renombra `tu_paquete` en `pyproject.toml:15` y `CONTEXT.md` con tu dominio.

## Estructura

- `AGENTS.md` — aprobación previa + CI local↔GitHub
- `CONTEXT.md` — glosario puro (linter `\.py:\d+`)
- `docs/adr/0007*` — ADR Golden Path
- `docs/agents/` — `domain.md`, `triage-labels.md`, `issue-tracker.md`
- `harness/` — P-E-V + `check_context.py` + `plan.example.json`
- `.github/workflows/ci.yml` + `agent-review.yml` — CI `uv` + review `fromJSON`
- `CLAUDE.md` — `MUST impact/detect_changes`

## DoD

`CI fail rate <10%` + `harness verify verdict:ok risk:low` + `detect_changes` sin `HIGH` + `pdg:true` `status:current`.

Ver `docs/adr/0007-fusion-three-methodologies.md`.

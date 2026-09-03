---
description: Golden Path Fusión — Issue → triage → wayfinder? → to-tickets → gitnexus-plan → gitnexus-work+harness → reviews → merge humano
---

# Golden Path Fusión — `/golden-path $ARGUMENTS`

Pipeline único y obligatorio (ver `docs/adr/0007-fusion-three-methodologies.md`).
Respeta `AGENTS.md` aprobación previa: pausa y pide confirmación en cada gate `HITL`.
Nunca auto-ejecutes el siguiente paso sin aprobación explícita.
Para la ráfaga autónoma con panel único usa `/golden-auto`.

## Modo automático

La ráfaga autónoma con panel único vive en `/golden-auto`
(ver `docs/adr/0009-golden-path-auto.md`).

(Contenido del modo `--auto` movido a `.opencode/commands/golden-auto.md`.)

## Orden canónico (anti-solape)

1. **Triage.** Carga skill `triage`. Mueve el issue `needs-triage → ready-for-agent` (o `ready-for-human`/`needs-info`/`wontfix` según corresponda). Verifica el claim (reproduce bug), chequea redundancia por concepto y `.out-of-scope/`. Publica el agent brief. Mapa de labels: `docs/agents/triage-labels.md`. Tracker: `docs/agents/issue-tracker.md`.
2. **Boundary triage (gate anti-planificación cara).** Si la tarea es chica y acotada (1-2 archivos, sin decisiones de arquitectura, muy por debajo de ~35 turns) ofrece `gitnexus-work` en modo directo y deja que el usuario elija. Si hay niebla (destino difuso, >1 sesión) sigue a paso 3. Si el camino ya está claro, salta a paso 4.
3. **Wayfinder (solo con niebla).** Carga skill `wayfinder`. Regla `Plan, don't do`: produce mapa `wayfinder:map` + decision tickets (`research/prototype/grilling/task`), un ticket por sesión. Si no hay fog, no crees mapa.
4. **To-tickets (una sola vez).** Carga skill `to-tickets`. Trocea en vertical slices tracer-bullet con `Blocked by`. Presenta la lista y reitera hasta aprobación. Publica con label `ready-for-agent`. No re-slicear después en `gitnexus-plan §7`.
5. **Por cada ticket del frontier — gitnexus-plan.** Carga skill `gitnexus-plan`. `compact + freshness:accept` por defecto; `full + strict + PDG` solo en refactor/API compartida/seguridad/performance. Usa la escalera `query → context → impact → trace → pdg_query + explain`, verifica en fuente (`source beats graph`). Escribe `docs/plans/YYYY-MM-DD-gitnexus-plan-<slug>.md` solo vía helper `write-plan`.
6. **Gate humano bloqueante.** Presenta objetivo, cambios propuestos, secuencia, riesgos, preguntas abiertas y ruta del plan. Opciones: Proceed to work / Stop here (+ Deepen si lo piden). Sin elección explícita no se ejecuta.
7. **Gitnexus-work (tdd dentro + harness verify).** Carga skill `gitnexus-work`. Re-ancla el plan a HEAD, rama `feat/<slug>`. Procedimiento `Build-current/index-current` antes de cada `impact` (`node .gitnexus/run.cjs analyze --index-only --pdg` si stale). Por paso: `impact upstream` (contabiliza todo `d=1`, `HIGH/CRITICAL` se surfacea), implementa mínimo con loop `tdd` red→green en el seam acordado, tests desde los escenarios del plan, `verification_commands` (incluye `harness verify verdict:ok risk:low`), `detect_changes staged` → commit atómico. Final: `detect_changes all` + suite completa + DoD §13.
8. **Reviews combinados (una pasada).** Carga skills `gitnexus-review` y `code-review` en paralelo. `gitnexus-review`: blast-radius fuera del diff, taint (`explain`) y dependencias (`pdg_query`), tests faltantes, veredicto. `code-review`: dos ejes `Standards` vs `Spec` sin re-rankear entre ejes. Un solo fix-cycle; en el re-run solo se reporta.
9. **Merge humano.** El humano hace merge, cierra el issue con `## Answer` y actualiza `Decisions-so-far` del mapa. `trajectory.jsonl` queda en `done`.

## DoD Golden Path

- `CI fail rate <10%`, `uv sync --all-packages` local = `ci.yml`.
- `harness verify verdict:ok risk:low` sin `UNKNOWN` sin confirmar.
- `detect_changes` sin `HIGH` ignorado. `impact_ratio` solo observado.
- `pdg:true` y `status:current`.

## Prohibido

- Saltar `impact before edit` / `detect_changes before commit`.
- Doble slice (épica en `to-tickets` y de nuevo en `gitnexus-plan`).
- `gitnexus-lfg` completo + lanes sueltas a la vez.
- Commitear sin gate humano previo en pasos destructivos o red no listada.

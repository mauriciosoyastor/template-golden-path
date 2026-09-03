# Glosario de dominio — [TU PROYECTO]

Glosario y nada más: sin specs, sin implementación. Los términos se agregan a medida que se resuelven.

## Términos del proyecto

- **Roadmap de aprendizaje ejecutable**: el destino de este esfuerzo.
- **Hito**: proyecto mínimo que corre y el aprendiz lo entiende.

## Términos de la fusión Golden Path (ADR-0007)

- **Golden Path Fusión**: pipeline único y obligatorio `Issue → triage → wayfinder? → to-tickets → gitnexus-plan → gitnexus-work(+harness verify) → reviews → merge humano`. Se invoca con `/golden-path` (`/golden-auto` para ráfaga autónoma con panel Hecho/Pendiente); `pytest` solo corre el seam `CI+Harness` y nunca ejecuta skills (las skills viven a nivel agente). Reglas anti-solape: `wayfinder` solo con niebla, `to-tickets` trocea una vez, un solo fix-cycle de reviews. Single-writer `trajectory.jsonl`, `sandbox-edit` default. Orden canónico de (1) Matt Pocock (2) GitNexus (3) repo más Harness; ver ADR-0007, ADR-0008 y ADR-0009.
- **DoD Golden Path**: `CI fail rate <10%` + `harness verify verdict:ok risk:low` sin `UNKNOWN` sin confirmar + `detect_changes` sin `HIGH` ignorado + `pdg:true` `status:current`.
- **Linter de Documentación**: regla `\.py:\d+` sobre `CONTEXT.md` que prohíbe anclas `archivo:línea` efímeras; detalles viven en ADRs/prototypes.

<!-- Agrega tus términos de dominio debajo, sin anclas .py:línea -->

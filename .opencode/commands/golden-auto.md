---
description: Golden Path automático — ráfaga con defaults, auto-repair N=3 y panel único Hecho / Pendiente tu OK
---

# Golden Auto — `/golden-auto $ARGUMENTS`

Ráfaga autónoma del Golden Path Fusión (ver `docs/adr/0007-fusion-three-methodologies.md`,
`docs/adr/0009-golden-path-auto.md`). Invocarlo equivale a: "aprueba por
adelantado pasos locales y defaults recomendados; push/PR/close/merge siempre
con mi OK". Sin esa equivalencia no uses este comando: usa `/golden-path`.

## Auto-selección permitida (solo local y reversible)

Investiga y construye de corrido, sin preguntas intermedias:

1. **Triage + boundary.** Carga skill `triage`. Si hay niebla sigue a wayfinder;
   si la tarea es chica usa `gitnexus-work` directo; si el camino está claro
   salta a `to-tickets`.
2. **Wayfinder (solo con niebla).** Carga skill `wayfinder`, modo *chart the map*.
   Dispara subagentes `research` en paralelo (AFK). Los tickets `grilling` y
   `prototype` son HITL: se crean y quedan abiertos en la frontera, nunca te
   auto-respondas; van al panel como sesiones pendientes con el humano.
3. **To-tickets (una vez).** Carga skill `to-tickets`, acepta tu propio corte
   recomendado.
4. **Gitnexus-plan (por ticket).** Carga skill `gitnexus-plan`, profundidad
   `Standard` salvo que el caso pida otra (`full + strict + PDG` en
   refactor/API compartida/seguridad/performance). Escalera
   `query → context → impact → trace → pdg_query + explain`; escribe el plan
   solo vía helper `write-plan`.
5. **Work + reviews.** Carga `gitnexus-work`: rama `feat/<slug>`,
   `Build-current/index-current` antes de cada `impact`, `tdd` red→green,
   `harness verify verdict:ok risk:low`, `detect_changes` → commit atómico.
   Auto-reparación: máximo 3 reintentos por paso; al 3er fallo el issue pasa a
   `needs-human-attention` y se sigue con lo demás. Luego `gitnexus-review` +
   `code-review` en paralelo, un solo fix-cycle.

## Nunca auto (pendientes remotos)

Publicar tickets en GitHub, `git push`, `gh pr create`, `gh issue close`,
merge. Al terminar entrega panel único con dos zonas — **Hecho** (brief,
tickets, plan, rama + commits locales, verify, review, tickets HITL
pendientes) y **Pendiente tu OK** (lista numerada de escrituras remotas).
Ejecuta las pendientes solo con elección explícita del usuario.

## DoD y prohibiciones

Mismas que `/golden-path`: `CI fail rate <10%`, `verify ok/low`,
`detect_changes` sin `HIGH` ignorado, `pdg:true status:current`.
Prohibido: saltar `impact before edit` / `detect_changes before commit`,
doble slice, `lfg` + lanes sueltas a la vez.

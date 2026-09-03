# Instrucciones del proyecto

## Regla obligatoria: aprobación previa

- **Nunca** ejecutes un proceso ni continúes con la siguiente tarea sin la aprobación explícita del usuario.
- Antes de ejecutar, editar, instalar, commitear o iniciar cualquier acción que modifique el sistema o el repositorio, propone el plan y espera confirmación.
- Si un paso tiene varias opciones, presenta las opciones y deja que el usuario elija.
- Esta regla aplica incluso si el usuario pidió una tarea larga con varios pasos: cada paso se ejecuta solo tras aprobación.

## Regla de CI local↔GitHub (no se vuelve a equivocar)

- **Raíz instalable**: `pyproject.toml` debe exponer `tu_paquete` vía `[tool.setuptools.packages.find] where=["."] include=["tu_paquete*"]` + `uv.lock` commiteado. `uv sync --all-packages` (no `--group dev`) en CI.
- **Ancla pytest**: `conftest.py` en la raíz + `[tool.pytest.ini_options] pythonpath = ["."]`. No borrar ninguno.
- **Mypy**: `explicit_package_bases = true`, `disallow_untyped_decorators = false`, `warn_unused_ignores = false`, y `[[tool.mypy.overrides]] ignore_missing_imports` para tus deps con stubs faltantes. Antes de push: `uv run ruff format . && uv run ruff check --fix . && uv run mypy tu_paquete && uv run pytest -q`.
- **Ruff F821 en tests**: si un test llama un símbolo de otro módulo, importalo en ese scope. Ver `docs/agents/lessons/0001-ruff-f821-imports-en-tests.md`.
- **Workflows GHA**: en `if:` no uses `\| int` (jq). Usá `fromJSON(steps.*.outputs.*)`. Ver `docs/agents/lessons/0002-gha-expresiones-sin-pipe-int.md`.
- **Artefactos**: no stagear `node_modules/`, `dist/`, `trajectory.jsonl`, `.opencode/node_modules/`. Ver `docs/agents/lessons/0004-gitignore-artefactos-agentes.md`.
- **Overrides temporales**: al aterrizar un módulo, retirar `ignore_missing_imports` / skips asociados. Ver `docs/agents/lessons/0005-mypy-overrides-temporales.md`.

Índice: `docs/agents/lessons/README.md`.

#!/usr/bin/env bash
set -e
echo "Golden Path init — renombra tu_paquete y CONTEXT.md"
read -p "Nombre paquete (ej. mi_app): " PKG
if [ -n "$PKG" ]; then
  mv tu_paquete "$PKG" 2>/dev/null || true
  sed -i "s/tu_paquete/$PKG/g" pyproject.toml .github/workflows/ci.yml harness/plan.example.json 2>/dev/null || true
fi
echo "Listo. Ejecuta: uv sync --all-packages && node .gitnexus/run.cjs analyze --index-only"

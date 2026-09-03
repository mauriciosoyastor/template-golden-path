"""Seam único Golden Path — genérico."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_golden_path_configs_exist() -> None:
    assert (REPO / ".gitnexusrc").exists()
    assert '"pdg": true' in (REPO / ".gitnexusrc").read_text(encoding="utf-8")
    assert (REPO / "CONTEXT.md").exists()
    assert (REPO / "docs" / "agents" / "domain.md").exists()
    assert "Golden Path" in (REPO / "CONTEXT.md").read_text(encoding="utf-8")


def test_harness_importable() -> None:
    import harness.harness as h

    assert hasattr(h, "TrajectoryEntry")
    assert hasattr(
        h.TrajectoryEntry(run_id="x", ts="x", phase="x", tier="x", intent="x"),
        "removed_tools",
    )

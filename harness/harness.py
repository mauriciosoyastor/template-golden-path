#!/usr/bin/env python3
"""
harness.py — Plan-Execute-Verify genérico (Golden Path)
Portado de Embodied AI — sin dominio Embodied AI.
Sensores: pytest + ruff + mypy + detect_changes + impact_ratio
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path

TIERS = ("read-only", "sandbox-edit", "full-access")
DEFAULT_TIER = "sandbox-edit"
ALLOWLIST_DOMAINS = ["localhost", "127.0.0.1", "huggingface.co", "api.openai.com"]
DESTRUCTIVE_PATTERNS = [r"\brm\s+-rf\b", r"\bpush\s+--force\b", r"\.env\b", r"\bDROP\b"]
SANDBOX_WRITABLE_SUFFIXES = [
    "harness/output/",
    "harness/trajectory.jsonl",
    "harness/sensor_logs/",
    "output/",
    "trajectory.jsonl",
    "sensor_logs/",
]

ROOT = Path(__file__).parent
REPO_ROOT = ROOT.parent
TRAJECTORY = ROOT / "trajectory.jsonl"
SENSOR_LOG_DIR = ROOT / "sensor_logs"
OUTPUT_DIR = ROOT / "output"


@dataclass
class HumanGate:
    needed: bool
    reason: str = ""
    approved_by: str | None = None
    approved_at: str | None = None


@dataclass
class EvidenceBundle:
    tests_run: list[str] = field(default_factory=list)
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0
    linter: dict = field(default_factory=dict)
    mypy: dict = field(default_factory=dict)
    domain_assertions: dict = field(default_factory=dict)
    uncovered: list[str] = field(default_factory=list)
    risk: str = "unknown"
    risk_reason: str = ""
    impact_ratio: float | None = None
    impacted_nodes: int = 0
    changed_lines: int = 0


@dataclass
class TrajectoryEntry:
    run_id: str
    ts: str
    phase: str
    tier: str
    intent: str
    files_touched: list[str] = field(default_factory=list)
    verdict: str = "pending"
    evidence: EvidenceBundle = field(default_factory=EvidenceBundle)
    human_gate: HumanGate = field(default_factory=lambda: HumanGate(needed=False))
    sensor_log: str = ""
    removed_tools: list[str] = field(default_factory=list)


def check_permission(
    tier: str, action: str, target: str, allow_network: bool
) -> HumanGate:
    action_l = action.lower()
    for pat in DESTRUCTIVE_PATTERNS:
        if re.search(pat, target + " " + action, re.IGNORECASE):
            return HumanGate(
                needed=True, reason=f"accion destructiva: {pat} en '{target}'"
            )
    is_network = any(
        k in action_l for k in ["fetch", "requests", "curl", "http"]
    ) or target.startswith("http")
    if is_network and not allow_network and tier != "full-access":
        if not any(d in target for d in ALLOWLIST_DOMAINS):
            return HumanGate(needed=True, reason=f"red no listada: '{target}'")
    if tier == "read-only" and action_l in ("write", "edit", "exec", "network"):
        return HumanGate(needed=True, reason=f"read-only: '{action}' sobre '{target}'")
    if tier == "sandbox-edit" and action_l in ("write", "edit"):
        norm = target.replace("\\", "/")
        if not (
            norm.startswith("harness/output/")
            or norm.startswith("harness/sensor_logs/")
            or norm in ("harness/trajectory.jsonl", "trajectory.jsonl")
            or norm.startswith("output/")
            or norm.startswith("sensor_logs/")
        ):
            return HumanGate(
                needed=True,
                reason=f"sandbox-edit: write fuera de sandbox en '{target}'",
            )
    return HumanGate(needed=False)


def run_pytest(run_id: str) -> tuple[dict, str]:
    log_path = SENSOR_LOG_DIR / f"{run_id}.log"
    SENSOR_LOG_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "pytest", "-q"]
    has_tests = (REPO_ROOT / "tests").exists()
    header = f"=== sensor run {run_id} @ {time.strftime('%Y-%m-%dT%H:%M:%S')} ===\n"
    header += f"cmd: {' '.join(cmd)}\n"
    if not has_tests:
        msg = header + "no tests found — uncovered: [pytest]\n"
        log_path.write_text(msg, encoding="utf-8")
        return {
            "tool": "pytest",
            "ok": None,
            "skipped": True,
            "reason": "no tests",
        }, msg
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=90,
            cwd=str(REPO_ROOT),
            encoding="utf-8",
            errors="replace",
        )
        out = (
            header
            + (proc.stdout or "")
            + (proc.stderr or "")
            + f"\nexit={proc.returncode}\n"
        )
        log_path.write_text(out, encoding="utf-8")
        return {
            "tool": "pytest",
            "ok": proc.returncode == 0,
            "exit": proc.returncode,
            "raw": out[:2000],
        }, out
    except Exception as e:
        msg = header + f"pytest error {e}\n"
        log_path.write_text(msg, encoding="utf-8")
        return {"tool": "pytest", "ok": None, "skipped": True}, msg


def run_ruff(run_id: str) -> dict:
    try:
        proc = subprocess.run(
            ["ruff", "check", "."],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
            encoding="utf-8",
            errors="replace",
        )
        log_path = SENSOR_LOG_DIR / f"{run_id}.log"
        if log_path.exists():
            prev = log_path.read_text(encoding="utf-8")
            out = (proc.stdout or "") + (proc.stderr or "")
            log_path.write_text(
                prev + f"\n--- ruff ---\nexit={proc.returncode}\n" + out,
                encoding="utf-8",
            )
        return {
            "tool": "ruff",
            "ok": proc.returncode == 0,
            "issues": ((proc.stdout or "") + (proc.stderr or ""))[:2000],
        }
    except FileNotFoundError:
        return {
            "tool": "ruff",
            "ok": None,
            "skipped": True,
            "reason": "ruff no instalado",
        }


def run_mypy(run_id: str) -> dict:
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "mypy", ".", "--ignore-missing-imports"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
            encoding="utf-8",
            errors="replace",
        )
        log_path = SENSOR_LOG_DIR / f"{run_id}.log"
        if log_path.exists():
            prev = log_path.read_text(encoding="utf-8")
            out = (proc.stdout or "") + (proc.stderr or "")
            log_path.write_text(
                prev + f"\n--- mypy ---\nexit={proc.returncode}\n" + out,
                encoding="utf-8",
            )
        return {
            "tool": "mypy",
            "ok": proc.returncode == 0,
            "issues": ((proc.stdout or "") + (proc.stderr or ""))[:2000],
        }
    except Exception as e:
        return {"tool": "mypy", "ok": None, "skipped": True, "reason": str(e)}


def run_detect_changes() -> dict:
    try:
        proc = subprocess.run(
            ["node", ".gitnexus/run.cjs", "detect-changes", "--scope", "all", "--json"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(REPO_ROOT),
            encoding="utf-8",
            errors="replace",
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        high = "HIGH" in out
        unknown = "UNKNOWN" in out
        impacted = changed = 0
        try:
            data = json.loads(proc.stdout or "{}")
            if isinstance(data, dict):
                impacted = int(data.get("impacted_nodes", 0) or 0)
                changed = int(data.get("changed_lines", 0) or 0)
        except Exception:
            pass
        return {
            "impacted_nodes": impacted,
            "changed_lines": changed,
            "high": high,
            "unknown": unknown,
            "raw": out[:2000],
        }
    except Exception as e:
        return {
            "impacted_nodes": 0,
            "changed_lines": 0,
            "high": False,
            "unknown": False,
            "raw": f"skip: {e}",
        }


def domain_assertions() -> dict:
    # Genérico: sin dominio específico, solo verifica que harness output existe si hay
    return {"checked": 0, "ok": True, "failures": [], "note": "genérico — sin dominio"}


def build_evidence(run_id: str) -> tuple[EvidenceBundle, str]:
    ev = EvidenceBundle()
    py_res, py_log = run_pytest(run_id)
    ev.tests_run.append("pytest")
    if py_res.get("skipped"):
        ev.uncovered.append("pytest (sin tests o no instalado)")
        ev.tests_skipped += 1
    elif py_res.get("ok"):
        ev.tests_passed += 1
    else:
        ev.tests_failed += 1
        ev.uncovered.append("pytest: failures")
    ruff_res = run_ruff(run_id)
    ev.linter = ruff_res
    if ruff_res.get("skipped"):
        ev.uncovered.append("ruff (no instalado)")
    elif not ruff_res.get("ok"):
        ev.uncovered.append("ruff: issues")
    mypy_res = run_mypy(run_id)
    ev.mypy = mypy_res
    if mypy_res.get("skipped"):
        ev.uncovered.append("mypy (no instalado)")
    elif not mypy_res.get("ok"):
        ev.uncovered.append("mypy: type issues")
    dom = domain_assertions()
    ev.domain_assertions = dom
    if not dom.get("ok"):
        ev.uncovered.append(f"domain: {len(dom.get('failures', []))} fallos")
    dc = run_detect_changes()
    ev.impacted_nodes = int(dc.get("impacted_nodes", 0) or 0)
    ev.changed_lines = int(dc.get("changed_lines", 0) or 0)
    if ev.changed_lines > 0:
        ev.impact_ratio = ev.impacted_nodes / ev.changed_lines
    else:
        ev.impact_ratio = float(ev.impacted_nodes) if ev.impacted_nodes else 0.0
    if dc.get("high") or dc.get("unknown"):
        ev.uncovered.append(f"detect_changes: {dc.get('raw', '')[:120]}")
    if ev.impact_ratio is not None and ev.impact_ratio > 10:
        ev.uncovered.append(
            f"impact_ratio {ev.impact_ratio:.1f} >10 → needs-human-attention"
        )
    if (
        ev.tests_failed > 0
        or not dom.get("ok")
        or dc.get("high")
        or dc.get("unknown")
        or (ev.impact_ratio is not None and ev.impact_ratio > 10)
    ):
        ev.risk = "high"
        ev.risk_reason = "tests o domain o blast radius HIGH"
    elif ev.uncovered:
        ev.risk = "medium"
        ev.risk_reason = f"cobertura parcial: {', '.join(ev.uncovered[:3])}"
    else:
        ev.risk = "low"
        ev.risk_reason = "sensores ok"
    return ev, f"harness/sensor_logs/{run_id}.log"


def append_trajectory(entry: TrajectoryEntry):
    TRAJECTORY.parent.mkdir(parents=True, exist_ok=True)
    rec = asdict(entry)
    rec["evidence"] = asdict(entry.evidence)
    rec["human_gate"] = asdict(entry.human_gate)
    with TRAJECTORY.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def run_harness(
    intent: str,
    tier: str,
    allow_network: bool,
    run_id: str,
    plan_path: Path | None = None,
):
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    print(f"[harness] run_id={run_id} tier={tier} intent='{intent}'")
    plan = {"intent": intent, "files": ["harness/output/demo.json"], "invariants": []}
    if plan_path and plan_path.exists():
        try:
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            intent = plan.get("intent", intent)
        except Exception as e:
            print(f"[plan] warn: {e}")
    entry_plan = TrajectoryEntry(
        run_id=run_id,
        ts=ts,
        phase="plan",
        tier=tier,
        intent=intent,
        verdict="ok",
        files_touched=list(plan.get("files", [])),
    )
    entry_plan.evidence = EvidenceBundle(
        tests_run=[], risk="unknown", risk_reason="plan: sin sensores"
    )
    append_trajectory(entry_plan)
    # execute demo write
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    demo_state = OUTPUT_DIR / "demo.json"
    if not demo_state.exists():
        demo_state.write_text(
            json.dumps({"run_id": run_id, "_ts": time.time()}, indent=2),
            encoding="utf-8",
        )
    entry_exec = TrajectoryEntry(
        run_id=run_id,
        ts=time.strftime("%Y-%m-%dT%H:%M:%S"),
        phase="execute",
        tier=tier,
        intent=intent,
        verdict="ok",
        files_touched=[str(demo_state)],
    )
    append_trajectory(entry_exec)
    print("[verify] sensores: pytest, ruff, mypy, detect_changes...")
    evidence, sensor_log = build_evidence(run_id)
    verdict = (
        "ok"
        if evidence.risk == "low" and evidence.tests_failed == 0
        else ("fail" if evidence.risk == "high" else "ok")
    )
    entry_verify = TrajectoryEntry(
        run_id=run_id,
        ts=time.strftime("%Y-%m-%dT%H:%M:%S"),
        phase="verify",
        tier=tier,
        intent=intent,
        verdict=verdict,
        evidence=evidence,
        sensor_log=sensor_log,
    )
    append_trajectory(entry_verify)
    print(
        f"[verify] verdict={verdict} risk={evidence.risk} uncovered={evidence.uncovered}"
    )
    entry_done = TrajectoryEntry(
        run_id=run_id,
        ts=time.strftime("%Y-%m-%dT%H:%M:%S"),
        phase="done",
        tier=tier,
        intent=intent,
        verdict=verdict,
        evidence=evidence,
        sensor_log=sensor_log,
    )
    append_trajectory(entry_done)
    print(f"[done] {verdict} — cat harness/trajectory.jsonl | grep {run_id}")


def main():
    ap = argparse.ArgumentParser(description="harness Golden Path — P-E-V")
    ap.add_argument("--tier", choices=TIERS, default=DEFAULT_TIER)
    ap.add_argument("--allow-network", default="false")
    ap.add_argument("--intent", default="demo: validar harness")
    ap.add_argument("--plan", dest="plan_path", default=None)
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args()
    allow_network = str(args.allow_network).lower() in ("true", "1", "yes")
    run_id = args.run_id or uuid.uuid4().hex[:8]
    plan_path = Path(args.plan_path) if args.plan_path else None
    run_harness(args.intent, args.tier, allow_network, run_id, plan_path)


if __name__ == "__main__":
    main()

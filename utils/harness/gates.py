from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


class GateError(RuntimeError):
    pass


def run_gate(cwd: Path, gate: dict[str, Any], timeout: int = 900) -> dict[str, Any]:
    argv = gate.get("command")
    if not isinstance(argv, list) or not argv or not all(isinstance(x, str) for x in argv):
        raise GateError("Gate command must be a non-empty argv list")
    proc = subprocess.run(
        argv,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=gate.get("timeout", timeout),
    )
    return {
        "name": gate.get("name"),
        "command": argv,
        "returncode": proc.returncode,
        "passed": proc.returncode == 0,
        "stdout": proc.stdout[-12000:],
        "stderr": proc.stderr[-12000:],
    }


def run_named_gates(cwd: Path, names: list[str], catalog: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for name in names:
        if name not in catalog:
            raise GateError(f"Unknown gate: {name}")
        spec = dict(catalog[name])
        spec["name"] = name
        result = run_gate(cwd, spec)
        results.append(result)
        if not result["passed"]:
            break
    return results

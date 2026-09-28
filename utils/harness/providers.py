from __future__ import annotations

import json
import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ProviderError(RuntimeError):
    pass


@dataclass
class ProviderResult:
    payload: dict[str, Any]
    stdout: str = ""
    stderr: str = ""


def _extract_json(text: str) -> dict[str, Any] | None:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        value = json.loads(stripped)
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    candidate: dict[str, Any] | None = None
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            candidate = value
    return candidate


def build_prompt(envelope: dict[str, Any]) -> str:
    contract = {
        "status": "ok | pass | fail | blocked",
        "summary": "concise factual summary",
        "findings": [
            {
                "severity": "info | warning | blocker",
                "message": "finding",
                "files": ["relative/path"]
            }
        ],
        "requested_actions": ["optional follow-up"],
    }
    return (
        "You are one worker inside a repository agent harness. Follow the role, scope, invariants and task exactly. "
        "Do not claim validation you did not run. Do not run git commit, git checkout, git switch, git merge, git rebase, or git reset; the harness owns Git history. "
        "Do not perform deploys, merges to main, credential rotation, force pushes, or external production mutations. When you finish, output one JSON object matching output_contract.\n\n"
        + json.dumps({**envelope, "output_contract": contract}, ensure_ascii=False, indent=2)
    )


def _safe_env(provider: dict[str, Any], task_id: str) -> dict[str, str]:
    safe_names = {
        "PATH", "HOME", "USER", "USERPROFILE", "SYSTEMROOT", "WINDIR",
        "TEMP", "TMP", "TMPDIR", "SHELL", "COMSPEC", "LANG", "LC_ALL",
        "TERM", "XDG_CONFIG_HOME",
    }
    safe_names.update(provider.get("pass_env", []))
    env = {name: value for name, value in os.environ.items() if name in safe_names}
    env["AGENT_HARNESS_TASK_ID"] = task_id
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["NO_COLOR"] = "1"
    return env


def run_provider(provider: dict[str, Any], envelope: dict[str, Any], cwd: Path, timeout: int) -> ProviderResult:
    kind = provider.get("kind")
    if kind == "dry_run":
        return ProviderResult(
            payload={
                "status": "pass",
                "summary": f"Dry-run: {envelope['task']['id']} would run as {envelope['role']['name']}",
                "findings": [],
                "requested_actions": [],
            }
        )
    if kind != "env_command":
        raise ProviderError(f"Unsupported provider kind: {kind}")
    env_name = provider.get("env")
    command = os.environ.get(env_name or "", "").strip()
    if not command:
        raise ProviderError(
            f"Provider command is not configured. Set {env_name} to a local agent command that reads stdin."
        )
    argv = shlex.split(command)
    if not argv:
        raise ProviderError(f"{env_name} is empty after parsing")
    proc = subprocess.run(
        argv,
        cwd=cwd,
        input=build_prompt(envelope),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        env=_safe_env(provider, envelope["task"]["id"]),
    )
    if proc.returncode != 0:
        raise ProviderError(
            f"Provider command failed ({proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}"
        )
    payload = _extract_json(proc.stdout)
    if payload is None:
        payload = {
            "status": "blocked",
            "summary": proc.stdout.strip()[-8000:] or "Provider returned no structured result.",
            "findings": [],
            "requested_actions": ["Provider did not emit structured JSON; task cannot be accepted automatically."],
        }
    return ProviderResult(payload=payload, stdout=proc.stdout, stderr=proc.stderr)

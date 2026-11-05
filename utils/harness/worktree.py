from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from .git import run_git


@dataclass
class Workspace:
    task_id: str
    path: Path
    branch: str | None
    owned: bool


def slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._/-]+", "-", value).strip("-/")
    return value or "task"


def create_worktree(
    repo: Path,
    root: Path,
    run_id: str,
    task_id: str,
    base_ref: str,
    *,
    branch: bool = True,
) -> Workspace:
    branch_name = slug(f"agent/{run_id}/{task_id}") if branch else None
    path = root / slug(run_id) / slug(task_id).replace("/", "-")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError(f"Worktree path already exists: {path}")
    args = ["worktree", "add"]
    if branch_name:
        args += ["-b", branch_name]
    else:
        args += ["--detach"]
    args += [str(path), base_ref]
    proc = run_git(repo, args, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"Could not create worktree {path}: {proc.stderr.strip()}")
    return Workspace(task_id=task_id, path=path, branch=branch_name, owned=True)


def remove_worktree(repo: Path, workspace: Workspace) -> None:
    if not workspace.owned:
        return
    run_git(repo, ["worktree", "remove", "--force", str(workspace.path)], check=False)


class LockSet:
    def __init__(self, root: Path, names: list[str], owner: str):
        self.root = root
        self.names = sorted(set(names))
        self.owner = owner
        self.paths: list[Path] = []

    def __enter__(self):
        self.root.mkdir(parents=True, exist_ok=True)
        try:
            for name in self.names:
                safe = slug(name).replace("/", "-")
                path = self.root / f"{safe}.lock"
                fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    handle.write(self.owner)
                self.paths.append(path)
        except FileExistsError as exc:
            self.__exit__(None, None, None)
            raise RuntimeError(f"Scope lock is busy: {exc.filename}") from exc
        return self

    def __exit__(self, exc_type, exc, tb):
        for path in reversed(self.paths):
            path.unlink(missing_ok=True)
        self.paths.clear()

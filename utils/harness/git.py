from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Iterable


class GitError(RuntimeError):
    pass


def run_git(repo: Path, args: Iterable[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and proc.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc


def repo_root(repo: Path) -> Path:
    out = run_git(repo, ["rev-parse", "--show-toplevel"]).stdout.strip()
    return Path(out).resolve()


def head_sha(repo: Path, ref: str = "HEAD") -> str:
    return run_git(repo, ["rev-parse", ref]).stdout.strip()


def is_clean(repo: Path) -> bool:
    return not run_git(repo, ["status", "--porcelain"]).stdout.strip()


def changed_files(repo: Path) -> list[str]:
    tracked = set()
    for args in (["diff", "--name-only"], ["diff", "--cached", "--name-only"]):
        tracked.update(x for x in run_git(repo, args).stdout.splitlines() if x)
    untracked = run_git(repo, ["ls-files", "--others", "--exclude-standard"]).stdout.splitlines()
    tracked.update(x for x in untracked if x)
    return sorted(tracked)


def commit_all(repo: Path, message: str) -> str | None:
    files = changed_files(repo)
    if not files:
        return None
    run_git(repo, ["add", "-A"])
    proc = run_git(repo, ["commit", "-m", message], check=False)
    if proc.returncode != 0:
        raise GitError(f"Could not commit task changes: {proc.stderr.strip() or proc.stdout.strip()}")
    return head_sha(repo)


def current_branch(repo: Path) -> str | None:
    proc = run_git(repo, ["symbolic-ref", "--quiet", "--short", "HEAD"], check=False)
    return proc.stdout.strip() if proc.returncode == 0 else None


def reset_hard(repo: Path, ref: str = "HEAD") -> None:
    run_git(repo, ["reset", "--hard", ref])
    run_git(repo, ["clean", "-fd"])


def flatten_commits(repo: Path, base_sha: str) -> None:
    """Turn provider-created commits back into uncommitted changes for policy inspection."""
    run_git(repo, ["reset", "--mixed", base_sha])

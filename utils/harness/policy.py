from __future__ import annotations

import fnmatch
from pathlib import PurePosixPath
from typing import Iterable


APPROVAL_LEVELS = {"L0": 0, "L1": 1, "L2": 2, "L3": 3}


class PolicyViolation(RuntimeError):
    pass


def normalize_path(path: str) -> str:
    value = PurePosixPath(path.replace("\\", "/")).as_posix()
    while value.startswith("./"):
        value = value[2:]
    if value.startswith("../") or value == ".." or value.startswith("/"):
        raise PolicyViolation(f"Unsafe repository path: {path}")
    return value


def matches(path: str, patterns: Iterable[str]) -> bool:
    normalized = normalize_path(path)
    return any(fnmatch.fnmatchcase(normalized, p) for p in patterns)


def effective_scope(role_scope: list[str], task_scope: list[str] | None) -> tuple[list[str], list[str] | None]:
    return role_scope, task_scope


def scope_violations(changed: Iterable[str], role_scope: list[str], task_scope: list[str] | None) -> list[str]:
    bad: list[str] = []
    for path in changed:
        p = normalize_path(path)
        if role_scope and not matches(p, role_scope):
            bad.append(p)
            continue
        if task_scope and not matches(p, task_scope):
            bad.append(p)
    return sorted(set(bad))


def protected_violations(changed: Iterable[str], protected: list[dict], approval: str) -> list[str]:
    have = APPROVAL_LEVELS.get(approval, -1)
    bad: list[str] = []
    for path in changed:
        p = normalize_path(path)
        for rule in protected:
            if fnmatch.fnmatchcase(p, rule["pattern"]):
                need = APPROVAL_LEVELS[rule.get("requires", "L3")]
                if have < need:
                    bad.append(f"{p} (requires {rule.get('requires', 'L3')})")
    return sorted(set(bad))


def validate_patterns(patterns: Iterable[str]) -> None:
    for pattern in patterns:
        if not pattern or pattern.startswith("/") or ".." in PurePosixPath(pattern).parts:
            raise PolicyViolation(f"Unsafe scope pattern: {pattern}")

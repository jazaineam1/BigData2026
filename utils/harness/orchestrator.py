from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import load_harness, load_policy
from .gates import run_named_gates
from .git import changed_files, commit_all, current_branch, flatten_commits, head_sha, is_clean, reset_hard, run_git
from .policy import APPROVAL_LEVELS, protected_violations, scope_violations, validate_patterns
from .providers import run_provider
from .worktree import LockSet, Workspace, create_worktree, remove_worktree, slug


SUCCESS = {"ok", "pass", "passed", "planned", "success"}
FAILURE = {"fail", "failed", "blocked", "error"}


class HarnessRunError(RuntimeError):
    pass


@dataclass
class RunOutcome:
    run_id: str
    status: str
    results: dict[str, dict[str, Any]]
    workspaces: dict[str, Workspace]
    run_dir: Path


def validate_pipeline(pipeline: dict[str, Any], harness: dict[str, Any]) -> None:
    tasks = pipeline.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise HarnessRunError("Pipeline must contain a non-empty tasks list")
    by_id: dict[str, dict[str, Any]] = {}
    for task in tasks:
        if not isinstance(task, dict) or not task.get("id"):
            raise HarnessRunError("Every task must be an object with id")
        tid = str(task["id"])
        if tid in by_id:
            raise HarnessRunError(f"Duplicate task id: {tid}")
        by_id[tid] = task
        deps = task.get("depends_on", [])
        if not isinstance(deps, list):
            raise HarnessRunError(f"{tid}: depends_on must be a list")
        scope = task.get("scope", [])
        if scope:
            validate_patterns(scope)
        if task.get("type", "agent") == "agent":
            role = task.get("role")
            if role not in harness.get("roles", {}):
                raise HarnessRunError(f"{tid}: unknown role {role}")
    for tid, task in by_id.items():
        for dep in task.get("depends_on", []):
            if dep not in by_id:
                raise HarnessRunError(f"{tid}: unknown dependency {dep}")
        source = task.get("workspace_from")
        if source and source not in by_id:
            raise HarnessRunError(f"{tid}: workspace_from references unknown task {source}")

    remaining = {tid: set(task.get("depends_on", [])) for tid, task in by_id.items()}
    done: set[str] = set()
    while len(done) < len(remaining):
        ready = [tid for tid, deps in remaining.items() if tid not in done and deps <= done]
        if not ready:
            cycle = sorted(set(remaining) - done)
            raise HarnessRunError(f"Pipeline dependency cycle: {', '.join(cycle)}")
        done.update(ready)


def plan_waves(pipeline: dict[str, Any], max_concurrency: int) -> list[list[str]]:
    tasks = {str(t["id"]): t for t in pipeline["tasks"]}
    done: set[str] = set()
    waves: list[list[str]] = []
    while len(done) < len(tasks):
        ready = sorted(
            tid
            for tid, task in tasks.items()
            if tid not in done and set(task.get("depends_on", [])) <= done
        )
        if not ready:
            raise HarnessRunError("Pipeline has a dependency cycle")
        for idx in range(0, len(ready), max(1, max_concurrency)):
            chunk = ready[idx : idx + max(1, max_concurrency)]
            waves.append(chunk)
            done.update(chunk)
    return waves


def _utc_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def _result_status(payload: dict[str, Any]) -> str:
    return str(payload.get("status", "ok")).lower()


def _role_instructions(repo: Path, harness: dict[str, Any], role: str) -> str:
    spec = harness["roles"][role]
    path = repo / spec["instructions"]
    return path.read_text(encoding="utf-8")


def _approval_at_least(have: str, need: str) -> bool:
    return APPROVAL_LEVELS.get(have, -1) >= APPROVAL_LEVELS.get(need, 999)


class Orchestrator:
    def __init__(
        self,
        repo: Path,
        *,
        approval: str = "L1",
        provider_override: str | None = None,
        max_concurrency: int | None = None,
        allow_dirty: bool = False,
        cleanup: bool = False,
    ):
        self.repo = repo.resolve()
        self.harness = load_harness(self.repo)
        self.write_policy = load_policy(self.repo, "write-scopes.yaml")
        self.approval_policy = load_policy(self.repo, "approval-gates.yaml")
        self.quality_policy = load_policy(self.repo, "quality-gates.yaml")
        self.approval = approval
        self.provider_override = provider_override
        self.max_concurrency = max_concurrency or int(self.harness.get("runtime", {}).get("max_concurrency", 3))
        self.allow_dirty = allow_dirty
        self.cleanup = cleanup
        self._mutex = threading.Lock()

    def run(self, pipeline: dict[str, Any], goal: str, run_id: str | None = None) -> RunOutcome:
        validate_pipeline(pipeline, self.harness)
        if not self.allow_dirty and not is_clean(self.repo):
            raise HarnessRunError("Repository working tree is dirty. Commit/stash it or pass --allow-dirty.")

        run_id = slug(run_id or _utc_run_id()).replace("/", "-")
        runtime = self.harness["runtime"]
        runs_root = self.repo / runtime["runs_dir"]
        worktrees_root = self.repo / runtime["worktrees_dir"]
        locks_root = self.repo / runtime["locks_dir"]
        run_dir = runs_root / run_id
        if run_dir.exists():
            raise HarnessRunError(f"Run already exists: {run_dir}")
        run_dir.mkdir(parents=True)

        base_ref = str(pipeline.get("base_ref", "HEAD"))
        base_sha = head_sha(self.repo, base_ref)
        _write_json(
            run_dir / "run.json",
            {
                "run_id": run_id,
                "pipeline": pipeline.get("id"),
                "pipeline_path": pipeline.get("__path__"),
                "goal": goal,
                "base_ref": base_ref,
                "base_sha": base_sha,
                "approval": self.approval,
                "provider_override": self.provider_override,
                "status": "running",
            },
        )

        tasks = {str(t["id"]): t for t in pipeline["tasks"]}
        results: dict[str, dict[str, Any]] = {}
        workspaces: dict[str, Workspace] = {}
        pending = set(tasks)

        try:
            while pending:
                ready = sorted(
                    tid for tid in pending if set(tasks[tid].get("depends_on", [])) <= set(results)
                )
                if not ready:
                    raise HarnessRunError("No runnable tasks remain; dependency graph is inconsistent")

                skipped = []
                runnable = []
                for tid in ready:
                    dep_results = [results[d] for d in tasks[tid].get("depends_on", [])]
                    if any(r.get("status") not in SUCCESS for r in dep_results):
                        results[tid] = {
                            "task_id": tid,
                            "status": "skipped",
                            "summary": "Skipped because a dependency failed or was blocked.",
                        }
                        _write_json(run_dir / "tasks" / tid / "output.json", results[tid])
                        skipped.append(tid)
                    else:
                        runnable.append(tid)
                for tid in skipped:
                    pending.remove(tid)

                if not runnable:
                    continue

                chunk = runnable[: self.max_concurrency]
                with ThreadPoolExecutor(max_workers=len(chunk)) as pool:
                    futures = {
                        pool.submit(
                            self._run_task,
                            task=tasks[tid],
                            goal=goal,
                            run_id=run_id,
                            run_dir=run_dir,
                            base_sha=base_sha,
                            dependency_results={d: results[d] for d in tasks[tid].get("depends_on", [])},
                            workspaces=workspaces,
                            worktrees_root=worktrees_root,
                            locks_root=locks_root,
                        ): tid
                        for tid in chunk
                    }
                    for future in as_completed(futures):
                        tid = futures[future]
                        try:
                            result, workspace = future.result()
                        except Exception as exc:
                            result = {
                                "task_id": tid,
                                "status": "failed",
                                "summary": str(exc),
                                "error_type": type(exc).__name__,
                            }
                            workspace = None
                        with self._mutex:
                            results[tid] = result
                            if workspace is not None:
                                workspaces[tid] = workspace
                        _write_json(run_dir / "tasks" / tid / "output.json", result)
                        pending.remove(tid)

            failed = [tid for tid, result in results.items() if result.get("status") not in SUCCESS]
            status = "failed" if failed else "passed"
            final = {
                "run_id": run_id,
                "status": status,
                "failed_tasks": failed,
                "branches": {tid: ws.branch for tid, ws in workspaces.items() if ws.branch},
                "results": results,
            }
            _write_json(run_dir / "final.json", final)
            return RunOutcome(run_id, status, results, workspaces, run_dir)
        finally:
            if self.cleanup:
                for workspace in list(workspaces.values()):
                    remove_worktree(self.repo, workspace)

    def _workspace_for_task(
        self,
        task: dict[str, Any],
        run_id: str,
        base_sha: str,
        workspaces: dict[str, Workspace],
        worktrees_root: Path,
    ) -> Workspace:
        source = task.get("workspace_from")
        mode = task.get("mode", "read")
        if source:
            if source not in workspaces:
                raise HarnessRunError(f"{task['id']}: workspace_from {source} has no workspace")
            ws = workspaces[source]
            if task.get("type", "agent") == "agent" and mode == "read":
                source_sha = head_sha(ws.path)
                with self._mutex:
                    return create_worktree(
                        self.repo,
                        worktrees_root,
                        run_id,
                        str(task["id"]),
                        source_sha,
                        branch=False,
                    )
            return Workspace(task_id=str(task["id"]), path=ws.path, branch=ws.branch, owned=False)
        if mode == "write" or task.get("type") == "integrate":
            if not _approval_at_least(self.approval, "L1"):
                raise HarnessRunError(f"{task['id']}: local writes require L1 approval")
            with self._mutex:
                return create_worktree(self.repo, worktrees_root, run_id, str(task["id"]), base_sha, branch=True)
        if task.get("type", "agent") == "agent":
            with self._mutex:
                return create_worktree(self.repo, worktrees_root, run_id, str(task["id"]), base_sha, branch=False)
        return Workspace(task_id=str(task["id"]), path=self.repo, branch=None, owned=False)

    def _run_task(
        self,
        *,
        task: dict[str, Any],
        goal: str,
        run_id: str,
        run_dir: Path,
        base_sha: str,
        dependency_results: dict[str, dict[str, Any]],
        workspaces: dict[str, Workspace],
        worktrees_root: Path,
        locks_root: Path,
    ) -> tuple[dict[str, Any], Workspace | None]:
        task_id = str(task["id"])
        task_dir = run_dir / "tasks" / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        workspace = self._workspace_for_task(task, run_id, base_sha, workspaces, worktrees_root)
        lock_names = list(task.get("locks", []))
        with LockSet(locks_root, lock_names, owner=f"{run_id}:{task_id}"):
            task_type = task.get("type", "agent")
            if task_type == "integrate":
                result = self._run_integrate(task, workspace, dependency_results)
            elif task_type == "command":
                result = self._run_command_task(task, workspace)
            elif task_type == "agent":
                result = self._run_agent_task(task, workspace, goal, dependency_results, task_dir)
            else:
                raise HarnessRunError(f"{task_id}: unsupported task type {task_type}")
        return result, workspace if workspace.path != self.repo else None

    def _run_agent_task(
        self,
        task: dict[str, Any],
        workspace: Workspace,
        goal: str,
        dependency_results: dict[str, dict[str, Any]],
        task_dir: Path,
    ) -> dict[str, Any]:
        task_id = str(task["id"])
        role = str(task["role"])
        role_spec = self.harness["roles"][role]
        provider_name = self.provider_override or task.get("provider") or role_spec.get("provider")
        if provider_name not in self.harness.get("providers", {}):
            raise HarnessRunError(f"{task_id}: unknown provider {provider_name}")
        provider = self.harness["providers"][provider_name]
        mode = task.get("mode", "read")

        before = changed_files(workspace.path)
        baseline_sha = head_sha(workspace.path)
        baseline_branch = current_branch(workspace.path)
        local_context: dict[str, str] = {}
        if role == "requirements":
            state = self.repo / ".local-docente" / "Estado_del_curso.md"
            if state.exists():
                local_context["Estado_del_curso.md"] = state.read_text(encoding="utf-8")
        envelope = {
            "goal": goal,
            "role": {
                "name": role,
                "instructions": _role_instructions(self.repo, self.harness, role),
            },
            "task": {
                "id": task_id,
                "objective": task.get("objective", ""),
                "mode": mode,
                "scope": task.get("scope", []),
                "invariants": sorted(set(self.harness.get("default_invariants", []) + task.get("invariants", []))),
                "approval": self.approval,
            },
            "dependency_results": dependency_results,
            "local_private_context": local_context,
            "repository": {
                "workspace": str(workspace.path),
                "base_sha": head_sha(workspace.path),
            },
        }
        _write_json(task_dir / "input.json", envelope)
        timeout = int(task.get("timeout", self.harness["runtime"].get("agent_timeout_seconds", 1800)))
        provider_result = run_provider(provider, envelope, workspace.path, timeout)
        _write_json(task_dir / "provider.json", provider_result.payload)

        provider_sha = head_sha(workspace.path)
        provider_branch = current_branch(workspace.path)
        if provider_branch != baseline_branch:
            return {
                "task_id": task_id,
                "status": "failed",
                "summary": "Agent changed Git branch/detached state. Agents must not manage Git history; the harness owns it.",
                "provider": provider_name,
            }
        history_changed = provider_sha != baseline_sha
        if history_changed:
            if mode == "write":
                flatten_commits(workspace.path, baseline_sha)
            else:
                reset_hard(workspace.path, baseline_sha)
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "summary": "Read-only agent modified Git history; its workspace was reset and the task failed.",
                    "provider": provider_name,
                }

        after = changed_files(workspace.path)
        new_changes = sorted(set(after) | set(before))
        if mode == "read" and new_changes != before:
            reset_hard(workspace.path, baseline_sha)
            return {
                "task_id": task_id,
                "status": "failed",
                "summary": "Read-only agent modified repository files; changes were discarded.",
                "changed_files": sorted(set(new_changes) - set(before)),
                "provider": provider_name,
            }

        if mode == "write":
            role_scope = list(self.write_policy.get("roles", {}).get(role, []))
            task_scope = list(task.get("scope", [])) or None
            violations = scope_violations(after, role_scope, task_scope)
            protected = protected_violations(after, self.write_policy.get("protected", []), self.approval)
            if violations or protected:
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "summary": "Write policy violation; task was not committed.",
                    "scope_violations": violations,
                    "protected_violations": protected,
                    "changed_files": after,
                    "provider": provider_name,
                }

        gate_names = list(task.get("gates", []))
        gate_results = run_named_gates(workspace.path, gate_names, self.quality_policy.get("gates", {})) if gate_names else []
        if any(not x["passed"] for x in gate_results):
            return {
                "task_id": task_id,
                "status": "failed",
                "summary": "One or more deterministic gates failed.",
                "changed_files": after,
                "gates": gate_results,
                "provider": provider_name,
                "agent": provider_result.payload,
            }

        commit_sha = None
        if mode == "write" and after and task.get("commit", True):
            if not _approval_at_least(self.approval, "L2"):
                return {
                    "task_id": task_id,
                    "status": "blocked",
                    "summary": "Changes are ready in an isolated worktree, but committing requires L2 approval.",
                    "changed_files": after,
                    "workspace": str(workspace.path),
                    "branch": workspace.branch,
                    "gates": gate_results,
                    "provider": provider_name,
                    "agent": provider_result.payload,
                }
            commit_sha = commit_all(workspace.path, f"agent({task_id}): {task.get('objective', role)}")

        agent_status = _result_status(provider_result.payload)
        status = "failed" if agent_status in FAILURE else "passed"
        return {
            "task_id": task_id,
            "status": status,
            "summary": provider_result.payload.get("summary", "Agent task completed."),
            "findings": provider_result.payload.get("findings", []),
            "requested_actions": provider_result.payload.get("requested_actions", []),
            "changed_files": after,
            "branch": workspace.branch,
            "commit_sha": commit_sha,
            "gates": gate_results,
            "provider": provider_name,
        }

    def _run_integrate(
        self,
        task: dict[str, Any],
        workspace: Workspace,
        dependency_results: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        task_id = str(task["id"])
        if not _approval_at_least(self.approval, "L2"):
            return {
                "task_id": task_id,
                "status": "blocked",
                "summary": "Integration creates Git commits and requires L2 approval.",
                "branch": workspace.branch,
            }
        merged: list[str] = []
        for dep, result in dependency_results.items():
            branch = result.get("branch")
            commit_sha = result.get("commit_sha")
            if not branch or not commit_sha:
                continue
            proc = run_git(
                workspace.path,
                ["merge", "--no-ff", branch, "-m", f"Integrate agent task {dep}"],
                check=False,
            )
            if proc.returncode != 0:
                run_git(workspace.path, ["merge", "--abort"], check=False)
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "summary": f"Merge conflict while integrating {dep}; no automatic conflict resolution attempted.",
                    "branch": workspace.branch,
                    "merged": merged,
                    "conflict_branch": branch,
                }
            merged.append(branch)
        return {
            "task_id": task_id,
            "status": "passed",
            "summary": f"Integrated {len(merged)} agent branch(es).",
            "branch": workspace.branch,
            "commit_sha": head_sha(workspace.path),
            "merged": merged,
        }

    def _run_command_task(self, task: dict[str, Any], workspace: Workspace) -> dict[str, Any]:
        task_id = str(task["id"])
        gate_names = list(task.get("gates", []))
        results = run_named_gates(workspace.path, gate_names, self.quality_policy.get("gates", {}))
        passed = all(x["passed"] for x in results)
        return {
            "task_id": task_id,
            "status": "passed" if passed else "failed",
            "summary": "All deterministic gates passed." if passed else "A deterministic gate failed.",
            "gates": results,
            "branch": workspace.branch,
            "commit_sha": head_sha(workspace.path),
        }

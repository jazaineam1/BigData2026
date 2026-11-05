from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from .config import HarnessConfigError, find_repo_root, load_harness, load_pipeline, load_policy
from .gates import run_named_gates
from .orchestrator import HarnessRunError, Orchestrator, plan_waves, validate_pipeline
from .policy import APPROVAL_LEVELS


def _repo() -> Path:
    return find_repo_root(Path.cwd())


def cmd_validate(args: argparse.Namespace) -> int:
    repo = _repo()
    harness = load_harness(repo)
    load_policy(repo, "write-scopes.yaml")
    load_policy(repo, "approval-gates.yaml")
    load_policy(repo, "quality-gates.yaml")
    pipelines = sorted((repo / ".harness" / "pipelines").glob("*.yaml"))
    for path in pipelines:
        pipeline = load_pipeline(repo, path)
        validate_pipeline(pipeline, harness)
    print(f"Harness config OK: {len(pipelines)} pipeline(s), {len(harness.get('roles', {}))} role(s)")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    repo = _repo()
    harness = load_harness(repo)
    checks = {
        "git": shutil.which("git") is not None,
        "python": shutil.which("python") is not None or shutil.which("python3") is not None,
        "AGENTS.md": (repo / "AGENTS.md").exists(),
        "harness config": (repo / ".harness" / "harness.yaml").exists(),
    }
    failed = False
    for label, ok in checks.items():
        print(f"{'OK' if ok else 'FAIL':4} {label}")
        failed |= not ok
    print("\nProviders:")
    for name, spec in harness.get("providers", {}).items():
        if spec.get("kind") == "dry_run":
            print(f"OK   {name}: built-in")
            continue
        env_name = spec.get("env", "")
        configured = bool(os.environ.get(env_name))
        print(f"{'OK' if configured else 'WARN':4} {name}: {env_name} {'set' if configured else 'not set'}")
    return 1 if failed else 0


def cmd_plan(args: argparse.Namespace) -> int:
    repo = _repo()
    harness = load_harness(repo)
    pipeline = load_pipeline(repo, args.pipeline)
    validate_pipeline(pipeline, harness)
    concurrency = args.max_concurrency or int(harness["runtime"].get("max_concurrency", 3))
    waves = plan_waves(pipeline, concurrency)
    print(f"Pipeline: {pipeline.get('id')}\nGoal: {args.goal or '(provided at run time)'}\n")
    for idx, wave in enumerate(waves, 1):
        print(f"Wave {idx}: {', '.join(wave)}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    repo = _repo()
    pipeline = load_pipeline(repo, args.pipeline)
    orch = Orchestrator(
        repo,
        approval=args.approval,
        provider_override=args.provider,
        max_concurrency=args.max_concurrency,
        allow_dirty=args.allow_dirty,
        cleanup=args.cleanup,
    )
    outcome = orch.run(pipeline, args.goal, run_id=args.run_id)
    print(json.dumps({
        "run_id": outcome.run_id,
        "status": outcome.status,
        "run_dir": str(outcome.run_dir.relative_to(repo)),
        "tasks": {k: v.get("status") for k, v in outcome.results.items()},
        "branches": {k: w.branch for k, w in outcome.workspaces.items() if w.branch},
    }, ensure_ascii=False, indent=2))
    return 0 if outcome.status == "passed" else 2


def cmd_gate(args: argparse.Namespace) -> int:
    repo = _repo()
    policy = load_policy(repo, "quality-gates.yaml")
    catalog = policy.get("gates", {})
    names = args.names or list(catalog)
    results = run_named_gates(repo, names, catalog)
    for result in results:
        print(f"{'PASS' if result['passed'] else 'FAIL'} {result['name']}")
        if not result["passed"]:
            if result["stdout"]:
                print(result["stdout"])
            if result["stderr"]:
                print(result["stderr"], file=sys.stderr)
            return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-harness", description="BigData2026 multi-agent engineering harness")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="validate harness configuration and all pipeline DAGs")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("doctor", help="check local prerequisites and provider configuration")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("plan", help="show execution waves without running agents")
    p.add_argument("pipeline")
    p.add_argument("--goal", default="")
    p.add_argument("--max-concurrency", type=int)
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("run", help="run a pipeline")
    p.add_argument("pipeline")
    p.add_argument("--goal", required=True)
    p.add_argument("--approval", choices=sorted(APPROVAL_LEVELS), default="L1")
    p.add_argument("--provider", help="override every agent provider, e.g. dry_run")
    p.add_argument("--max-concurrency", type=int)
    p.add_argument("--run-id")
    p.add_argument("--allow-dirty", action="store_true")
    p.add_argument("--cleanup", action="store_true")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("gate", help="run one or more deterministic quality gates")
    p.add_argument("names", nargs="*")
    p.set_defaults(func=cmd_gate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (HarnessConfigError, HarnessRunError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

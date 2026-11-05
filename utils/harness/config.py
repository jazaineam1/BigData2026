from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class HarnessConfigError(RuntimeError):
    pass


def load_structured(path: Path) -> Any:
    """Load JSON or YAML without making PyYAML a hard dependency.

    All repository-owned *.yaml files are written as JSON, which is valid YAML 1.2.
    If users later switch them to traditional YAML and PyYAML is installed, that works too.
    """
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError as json_error:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise HarnessConfigError(
                f"{path} is not JSON-form YAML. Install PyYAML or keep harness YAML files JSON-compatible."
            ) from json_error
        try:
            return yaml.safe_load(text)
        except Exception as exc:  # pragma: no cover - delegated parser detail
            raise HarnessConfigError(f"Could not parse {path}: {exc}") from exc


def find_repo_root(start: Path | None = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / ".git").exists():
            return candidate
    raise HarnessConfigError("Not inside a Git repository")


def harness_dir(repo: Path) -> Path:
    return repo / ".harness"


def load_harness(repo: Path) -> dict[str, Any]:
    path = harness_dir(repo) / "harness.yaml"
    if not path.exists():
        raise HarnessConfigError(f"Missing {path.relative_to(repo)}")
    data = load_structured(path)
    if not isinstance(data, dict):
        raise HarnessConfigError(".harness/harness.yaml must contain an object")
    return data


def load_policy(repo: Path, name: str) -> dict[str, Any]:
    path = harness_dir(repo) / "policies" / name
    data = load_structured(path)
    if not isinstance(data, dict):
        raise HarnessConfigError(f"{path.relative_to(repo)} must contain an object")
    return data


def load_pipeline(repo: Path, pipeline: str | Path) -> dict[str, Any]:
    path = Path(pipeline)
    if not path.is_absolute():
        if path.parts and path.parts[0] == ".harness":
            path = repo / path
        elif path.exists():
            path = path.resolve()
        else:
            path = harness_dir(repo) / "pipelines" / path
    if not path.exists():
        raise HarnessConfigError(f"Pipeline not found: {path}")
    data = load_structured(path)
    if not isinstance(data, dict):
        raise HarnessConfigError(f"{path} must contain an object")
    data["__path__"] = str(path)
    return data

import subprocess
import tempfile
import unittest
from pathlib import Path

from utils.harness.git import head_sha
from utils.harness.worktree import create_worktree, remove_worktree


def git(cwd: Path, *args: str):
    return subprocess.run(["git", *args], cwd=cwd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class WorktreeTests(unittest.TestCase):
    def test_detached_read_workspace_and_branch_write_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            git(repo, "init")
            git(repo, "config", "user.email", "harness-test.invalid")
            git(repo, "config", "user.name", "Harness Test")
            (repo / ".gitignore").write_text(".agent-worktrees/\n", encoding="utf-8")
            (repo / "README.md").write_text("base\n", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "base")
            base = head_sha(repo)
            root = repo / ".agent-worktrees"

            read_ws = create_worktree(repo, root, "run", "review", base, branch=False)
            self.assertIsNone(read_ws.branch)
            self.assertEqual(head_sha(read_ws.path), base)

            write_ws = create_worktree(repo, root, "run", "writer", base, branch=True)
            self.assertTrue(write_ws.branch.startswith("agent/run/writer"))
            self.assertEqual(head_sha(write_ws.path), base)

            remove_worktree(repo, read_ws)
            remove_worktree(repo, write_ws)


if __name__ == "__main__":
    unittest.main()

import unittest

from utils.harness.policy import protected_violations, scope_violations


class PolicyTests(unittest.TestCase):
    def test_role_and_task_scope_are_both_enforced(self):
        changed = ["lms/app.js", "infraestructura/lms/functions/x.ts"]
        bad = scope_violations(changed, ["lms/**", "tests/**"], ["lms/**"])
        self.assertEqual(bad, ["infraestructura/lms/functions/x.ts"])

    def test_protected_path_requires_approval(self):
        rules = [{"pattern": ".harness/**", "requires": "L2"}]
        self.assertTrue(protected_violations([".harness/harness.yaml"], rules, "L1"))
        self.assertFalse(protected_violations([".harness/harness.yaml"], rules, "L2"))


if __name__ == "__main__":
    unittest.main()

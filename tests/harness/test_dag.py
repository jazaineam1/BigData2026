import unittest

from utils.harness.orchestrator import SUCCESS, HarnessRunError, plan_waves, validate_pipeline


HARNESS = {"roles": {"requirements": {}, "qa": {}}}


class DagTests(unittest.TestCase):
    def test_parallel_wave_then_dependency(self):
        pipeline = {
            "tasks": [
                {"id": "a", "type": "agent", "role": "requirements"},
                {"id": "b", "type": "agent", "role": "qa"},
                {"id": "c", "type": "command", "depends_on": ["a", "b"]},
            ]
        }
        validate_pipeline(pipeline, HARNESS)
        self.assertEqual(plan_waves(pipeline, 3), [["a", "b"], ["c"]])

    def test_cycle_is_rejected(self):
        pipeline = {
            "tasks": [
                {"id": "a", "type": "agent", "role": "requirements", "depends_on": ["b"]},
                {"id": "b", "type": "agent", "role": "qa", "depends_on": ["a"]},
            ]
        }
        with self.assertRaises(HarnessRunError):
            validate_pipeline(pipeline, HARNESS)

    def test_skipped_is_not_success(self):
        self.assertNotIn("skipped", SUCCESS)

    def test_unknown_dependency_is_rejected(self):
        pipeline = {"tasks": [{"id": "a", "type": "command", "depends_on": ["missing"]}]}
        with self.assertRaises(HarnessRunError):
            validate_pipeline(pipeline, HARNESS)


if __name__ == "__main__":
    unittest.main()

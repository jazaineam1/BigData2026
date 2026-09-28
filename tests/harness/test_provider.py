import unittest
from unittest.mock import patch

from utils.harness.providers import _extract_json, _safe_env


class ProviderTests(unittest.TestCase):
    def test_extracts_json_from_agent_chatter(self):
        text = 'analysis omitted\n{"status":"pass","summary":"done","findings":[]}\n'
        value = _extract_json(text)
        self.assertEqual(value["status"], "pass")
        self.assertEqual(value["summary"], "done")

    def test_returns_none_without_object(self):
        self.assertIsNone(_extract_json("plain text"))

    def test_provider_environment_is_allowlisted(self):
        provider = {"pass_env": ["OPENAI_API_KEY"]}
        with patch.dict("os.environ", {"PATH": "/bin", "OPENAI_API_KEY": "ok", "AWS_SECRET_ACCESS_KEY": "nope"}, clear=True):
            env = _safe_env(provider, "t1")
        self.assertEqual(env["OPENAI_API_KEY"], "ok")
        self.assertNotIn("AWS_SECRET_ACCESS_KEY", env)
        self.assertEqual(env["AGENT_HARNESS_TASK_ID"], "t1")


if __name__ == "__main__":
    unittest.main()

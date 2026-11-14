from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from config.settings import Settings, SettingsError


class SettingsTests(unittest.TestCase):
    def test_reads_user_supplied_environment_names(self) -> None:
        env = {
            "OPENAI_API_KEY": "unit-test-provider-key",
            "DEFAULT_MODEL": "unit-test-model",
            "HUB_PORT": "8765",
            "HUB_API_KEY": "t" * 40,
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings.from_env()
        self.assertEqual(settings.model, "unit-test-model")
        self.assertEqual(settings.hub_port, 8765)
        self.assertEqual(settings.hub_api_key, "t" * 40)

    def test_rejects_short_gateway_token(self) -> None:
        env = {
            "OPENAI_API_KEY": "unit-test-provider-key",
            "HUB_API_KEY": "too-short",
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(SettingsError):
                Settings.from_env()

    def test_rejects_invalid_hub_port(self) -> None:
        env = {
            "OPENAI_API_KEY": "unit-test-provider-key",
            "HUB_PORT": "70000",
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(SettingsError):
                Settings.from_env()


if __name__ == "__main__":
    unittest.main()

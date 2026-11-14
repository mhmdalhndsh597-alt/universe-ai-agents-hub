from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents.content_agent import ContentAgent
from agents.support_agent import SupportAgent
from config.settings import Settings, SettingsError


class FakeClient:
    def __init__(self, text: str = "إجابة اختبارية") -> None:
        self.text = text
        self.calls: list[dict] = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.calls.append(kwargs)
        message = SimpleNamespace(content=self.text)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


def make_test_settings() -> Settings:
    return Settings(
        api_key="unit-test-placeholder",
        model="test-model",
        base_url=None,
        timeout_seconds=10.0,
        max_output_tokens=128,
    )


class AgentTests(unittest.TestCase):
    def test_support_drafts_reply_with_supplied_context(self) -> None:
        client = FakeClient("رد مقترح")
        agent = SupportAgent(make_test_settings(), client=client)
        result = agent.draft_reply("ما سعر الخدمة؟", "السعر يحدد بعد المعاينة")
        self.assertEqual(result, "رد مقترح")
        self.assertIn("السعر يحدد بعد المعاينة", client.calls[0]["messages"][1]["content"])
        self.assertEqual(client.calls[0]["model"], "test-model")

    def test_support_rejects_empty_message(self) -> None:
        agent = SupportAgent(make_test_settings(), client=FakeClient())
        with self.assertRaises(ValueError):
            agent.draft_reply("  ")

    def test_summary_includes_source_and_word_limit(self) -> None:
        client = FakeClient("ملخص")
        agent = ContentAgent(make_test_settings(), client=client)
        self.assertEqual(agent.summarize("نص المصدر", max_words=80), "ملخص")
        prompt = client.calls[0]["messages"][1]["content"]
        self.assertIn("80", prompt)
        self.assertIn("نص المصدر", prompt)

    def test_summary_rejects_invalid_word_limit(self) -> None:
        agent = ContentAgent(make_test_settings(), client=FakeClient())
        with self.assertRaises(ValueError):
            agent.summarize("نص", max_words=5)

    def test_draft_rejects_unsupported_format(self) -> None:
        agent = ContentAgent(make_test_settings(), client=FakeClient())
        with self.assertRaises(ValueError):
            agent.draft("موجز", format_name="unsupported")

    def test_missing_api_key_fails_without_exposing_value(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SettingsError):
                Settings.from_env()


if __name__ == "__main__":
    unittest.main()

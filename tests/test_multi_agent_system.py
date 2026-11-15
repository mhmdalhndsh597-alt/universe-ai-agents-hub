from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents.multi_agent_systems.code_review_system import CodeReviewSystem
from config.settings import Settings
from core.llm_provider import LLMService


class FakeClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = iter(responses)
        self.calls: list[dict] = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.calls.append(kwargs)
        text = next(self.responses)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=text))]
        )


def make_settings() -> Settings:
    return Settings(
        api_key="unit-test-placeholder",
        model="test-model",
        base_url=None,
        timeout_seconds=10.0,
        max_output_tokens=256,
    )


class CodeReviewSystemTests(unittest.TestCase):
    def test_writer_reviewer_collaborate_and_revise(self) -> None:
        client = FakeClient(
            [
                "def add(a, b): return a + b",
                "CHANGES_REQUESTED\nAdd type hints and a docstring.",
                "def add(a: int, b: int) -> int:\n    \"\"\"Return the sum.\"\"\"\n    return a + b",
                "APPROVED\nNo critical issues found; human verification is still required.",
            ]
        )
        system = CodeReviewSystem(make_settings(), client=client)

        outcome = system.run("اكتب دالة جمع رقمين.", max_revisions=1)

        self.assertTrue(outcome.approved)
        self.assertEqual(outcome.drafts_created, 2)
        self.assertTrue(outcome.requires_human_review)
        self.assertFalse(outcome.persisted)
        self.assertIn("def add(a: int", outcome.code)
        self.assertIn("Add type hints", client.calls[2]["messages"][1]["content"])
        self.assertEqual(len(client.calls), 4)

    def test_zero_revisions_returns_unapproved_draft(self) -> None:
        client = FakeClient(["draft code", "CHANGES_REQUESTED\nNeeds tests."])
        system = CodeReviewSystem(make_settings(), client=client)

        outcome = system.run("اكتب كودًا.", max_revisions=0)

        self.assertFalse(outcome.approved)
        self.assertEqual(outcome.drafts_created, 1)
        self.assertIn("Needs tests", outcome.review_feedback)
        self.assertEqual(len(client.calls), 2)

    def test_rejects_more_than_three_revisions(self) -> None:
        client = FakeClient([])
        system = CodeReviewSystem(make_settings(), client=client)

        with self.assertRaises(ValueError):
            system.run("اكتب كودًا.", max_revisions=4)
        self.assertEqual(client.calls, [])

    def test_rejects_empty_task(self) -> None:
        client = FakeClient([])
        system = CodeReviewSystem(make_settings(), client=client)

        with self.assertRaises(ValueError):
            system.run("   ")
        self.assertEqual(client.calls, [])

    def test_team_runs_safely_in_demo_mode_without_keys(self) -> None:
        progress: list[str] = []
        with patch.dict(os.environ, {}, clear=True):
            system = CodeReviewSystem(provider=LLMService())
            outcome = system.run("اكتب وظيفة تجريبية.", max_revisions=0, progress_callback=progress.append)

        self.assertFalse(outcome.approved)
        self.assertTrue(outcome.requires_human_review)
        self.assertIn("Demo Mode", outcome.review_feedback)
        self.assertEqual(outcome.drafts_created, 1)
        self.assertGreaterEqual(len(progress), 2)


if __name__ == "__main__":
    unittest.main()

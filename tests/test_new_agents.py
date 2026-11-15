from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents.automation.workflow_automator import WorkflowAutomatorAgent
from agents.content_creation.content_architect import ContentArchitectAgent
from agents.research.deep_researcher import DeepResearcherAgent
from core.llm_provider import LLMService


class FakeOpenAIClient:
    def __init__(self, text: str = "OpenAI test response") -> None:
        self.text = text
        self.calls: list[dict] = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self.text))]
        )


class FakeGeminiClient:
    def __init__(self, text: str = "Gemini test response") -> None:
        self.text = text
        self.calls: list[dict] = []
        self.models = SimpleNamespace(generate_content=self.generate_content)

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(text=self.text)


class NewAgentTests(unittest.TestCase):
    def test_three_agents_run_in_demo_mode_without_credentials(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            research = DeepResearcherAgent().run("أثر الطاقة المتجددة")
            workflow = WorkflowAutomatorAgent().run("تنظيم تقرير أسبوعي")
            content = ContentArchitectAgent().run("واجهات API آمنة")

        self.assertTrue(research.demo_mode)
        self.assertTrue(workflow.demo_mode)
        self.assertTrue(content.demo_mode)
        self.assertIn("أسئلة فرعية", research.text)
        self.assertIn("خطة أتمتة", workflow.text)
        self.assertIn("مسودة منشور", content.text)

    def test_openai_adapter_uses_injected_client(self) -> None:
        client = FakeOpenAIClient()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fake-test-key"}, clear=True):
            result = LLMService("openai", openai_client=client).complete(
                "system", "task", demo_response="demo"
            )

        self.assertEqual(result.provider, "openai")
        self.assertFalse(result.demo_mode)
        self.assertEqual(result.text, "OpenAI test response")
        self.assertEqual(client.calls[0]["model"], "gpt-4o-mini")

    def test_gemini_adapter_uses_injected_client(self) -> None:
        client = FakeGeminiClient()
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-test-key"}, clear=True):
            result = LLMService("gemini", gemini_client=client).complete(
                "system", "task", demo_response="demo"
            )

        self.assertEqual(result.provider, "gemini")
        self.assertFalse(result.demo_mode)
        self.assertEqual(result.text, "Gemini test response")
        self.assertIn("model", client.calls[0])

    def test_invalid_provider_is_rejected(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                LLMService("unknown")

    def test_selected_provider_without_any_key_uses_demo(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            service = LLMService("openai")
        self.assertTrue(service.demo_mode)

    def test_agent_rejects_empty_task(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                DeepResearcherAgent().run(" ")
            with self.assertRaises(ValueError):
                WorkflowAutomatorAgent().run(" ")
            with self.assertRaises(ValueError):
                ContentArchitectAgent().run(" ")


if __name__ == "__main__":
    unittest.main()

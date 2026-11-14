from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from api import create_app
from config.settings import Settings


class FakeSupportAgent:
    def draft_reply(self, message: str, context: str = "") -> str:
        return f"support-draft:{message}"


class FakeContentAgent:
    def summarize(self, text: str, max_words: int, language: str) -> str:
        return f"summary:{language}:{max_words}:{text[:20]}"

    def draft(self, brief: str, format_name: str, language: str) -> str:
        return f"draft:{format_name}:{language}:{brief[:20]}"


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        settings = Settings(
            api_key="unit-test-placeholder",
            model="test-model",
            base_url=None,
            timeout_seconds=10,
            max_output_tokens=128,
            hub_api_key="unit-test-hub-token",
        )
        app = create_app(
            settings,
            support_agent=FakeSupportAgent(),
            content_agent=FakeContentAgent(),
        )
        self.client = TestClient(app)
        self.headers = {"Authorization": "Bearer unit-test-hub-token"}

    def test_health_is_public_and_minimal(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_draft_rejects_missing_auth(self) -> None:
        response = self.client.post("/v1/support/draft", json={"message": "Hello"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "unauthorized")

    def test_draft_rejects_invalid_auth(self) -> None:
        response = self.client.post(
            "/v1/support/draft",
            headers={"Authorization": "Bearer incorrect"},
            json={"message": "Hello"},
        )
        self.assertEqual(response.status_code, 401)

    def test_support_draft_requires_human_review_and_is_not_saved(self) -> None:
        response = self.client.post(
            "/v1/support/draft",
            headers=self.headers,
            json={"message": "ما تفاصيل الخدمة؟", "context": "لا توجد سياسة سعر محددة."},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["requires_human_review"])
        self.assertFalse(response.json()["persisted"])
        self.assertIn("support-draft", response.json()["draft"])

    def test_content_summary_works_with_auth(self) -> None:
        response = self.client.post(
            "/v1/content/summarize",
            headers=self.headers,
            json={"text": "نص تجريبي", "max_words": 80, "language": "Arabic"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("summary:Arabic:80", response.json()["draft"])

    def test_content_draft_works_with_auth(self) -> None:
        response = self.client.post(
            "/v1/content/draft",
            headers=self.headers,
            json={"brief": "إطلاق خدمة إنتاج", "format": "social_post"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("draft:social_post:Arabic", response.json()["draft"])
        self.assertFalse(response.json()["persisted"])

    def test_oversized_content_is_rejected(self) -> None:
        response = self.client.post(
            "/v1/content/summarize",
            headers=self.headers,
            json={"text": "x" * 30_001},
        )
        self.assertEqual(response.status_code, 422)

    def test_oversized_request_body_is_rejected(self) -> None:
        body = b'{"message":"' + b"x" * (64 * 1024) + b'"}'
        response = self.client.post(
            "/v1/support/draft",
            headers=self.headers,
            content=body,
        )
        self.assertEqual(response.status_code, 413)

    def test_unknown_request_fields_are_rejected(self) -> None:
        response = self.client.post(
            "/v1/support/draft",
            headers=self.headers,
            json={"message": "Hello", "send_email": True},
        )
        self.assertEqual(response.status_code, 422)

    def test_missing_api_secret_disables_work_routes(self) -> None:
        settings = Settings(
            api_key="unit-test-placeholder",
            model="test-model",
            base_url=None,
            timeout_seconds=10,
            max_output_tokens=128,
            hub_api_key=None,
        )
        client = TestClient(create_app(settings))
        response = client.post(
            "/v1/support/draft",
            headers={"Authorization": "Bearer anything"},
            json={"message": "Hello"},
        )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "api_auth_not_configured")


if __name__ == "__main__":
    unittest.main()

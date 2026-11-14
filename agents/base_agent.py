"""Shared single-request LLM client used by the agents."""

from __future__ import annotations

from typing import Any

from config.settings import Settings


class AgentError(RuntimeError):
    """Safe, user-facing agent or provider error."""


class BaseAgent:
    def __init__(self, settings: Settings, client: Any | None = None) -> None:
        self.settings = settings
        if client is not None:
            self.client = client
            return

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise AgentError(
                "مكتبات المشروع غير مثبتة. شغّل: python -m pip install -r requirements.txt"
            ) from exc

        client_options: dict[str, Any] = {
            "api_key": settings.api_key,
            "timeout": settings.timeout_seconds,
            "max_retries": 2,
        }
        if settings.base_url:
            client_options["base_url"] = settings.base_url
        self.client = OpenAI(**client_options)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        if not user_prompt.strip():
            raise ValueError("النص المطلوب لا يمكن أن يكون فارغاً.")

        try:
            response = self.client.chat.completions.create(
                model=self.settings.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=self.settings.max_output_tokens,
            )
            content = response.choices[0].message.content
        except Exception as exc:
            # Do not propagate provider request dumps, headers, or possible credential material.
            raise AgentError(
                f"تعذر إكمال الطلب لدى مزود النموذج ({type(exc).__name__}). "
                "تحقق من إعدادات المزود والاتصال دون مشاركة المفتاح."
            ) from None

        if not isinstance(content, str) or not content.strip():
            raise AgentError("عاد مزود النموذج بإجابة فارغة؛ حاول بصياغة أخرى.")
        return content.strip()

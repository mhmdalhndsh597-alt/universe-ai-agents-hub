"""Minimal OpenAI/Gemini adapter with an explicit no-credential demo mode."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable


class LLMProviderError(RuntimeError):
    """Safe provider error that does not expose credentials or request payloads."""


@dataclass(frozen=True, slots=True)
class LLMResponse:
    text: str
    provider: str
    demo_mode: bool


class LLMService:
    """Call OpenAI or Gemini; return a labeled deterministic demo if no keys exist."""

    def __init__(
        self,
        provider: str | None = None,
        *,
        openai_client: Any | None = None,
        gemini_client: Any | None = None,
    ) -> None:
        requested = (provider or os.getenv("LLM_PROVIDER", "auto")).strip().lower()
        if requested not in {"auto", "openai", "gemini", "demo"}:
            raise ValueError("LLM_PROVIDER must be auto, openai, gemini, or demo.")

        self._openai_key = self._usable_key(os.getenv("OPENAI_API_KEY", ""))
        self._gemini_key = self._usable_key(os.getenv("GEMINI_API_KEY", "")) or self._usable_key(
            os.getenv("GOOGLE_API_KEY", "")
        )
        self._openai_client = openai_client
        self._gemini_client = gemini_client

        has_client = bool(openai_client or gemini_client)
        if requested == "demo" or (
            not self._openai_key and not self._gemini_key and not has_client
        ):
            self.provider = "demo"
        elif requested == "auto":
            self.provider = "openai" if (self._openai_key or openai_client) else "gemini"
        else:
            self.provider = requested

        if self.provider == "openai" and not (self._openai_key or self._openai_client):
            raise LLMProviderError("LLM_PROVIDER=openai يتطلب OPENAI_API_KEY مضبوطًا.")
        if self.provider == "gemini" and not (self._gemini_key or self._gemini_client):
            raise LLMProviderError("LLM_PROVIDER=gemini يتطلب GEMINI_API_KEY أو GOOGLE_API_KEY.")

    @property
    def demo_mode(self) -> bool:
        return self.provider == "demo"

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        demo_response: str | Callable[[], str],
    ) -> LLMResponse:
        if not system_prompt.strip() or not user_prompt.strip():
            raise ValueError("تعليمات النظام ومدخل المستخدم مطلوبان.")
        if self.provider == "demo":
            text = demo_response() if callable(demo_response) else demo_response
            return LLMResponse(text=text, provider="demo", demo_mode=True)

        try:
            if self.provider == "openai":
                client = self._openai_client or self._make_openai_client()
                response = client.chat.completions.create(
                    model=os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=int(os.getenv("MAX_OUTPUT_TOKENS", "1800")),
                    timeout=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
                )
                text = response.choices[0].message.content
            else:
                client = self._gemini_client or self._make_gemini_client()
                response = client.models.generate_content(
                    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                    contents=f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\nUSER INPUT:\n{user_prompt}",
                )
                text = response.text
        except Exception as exc:
            raise LLMProviderError(
                f"تعذر إكمال الطلب عبر مزود النموذج ({type(exc).__name__}). "
                "تحقق من إعدادات المزود والاتصال دون مشاركة المفتاح."
            ) from None

        if not isinstance(text, str) or not text.strip():
            raise LLMProviderError("أعاد مزود النموذج إجابة فارغة.")
        return LLMResponse(text=text.strip(), provider=self.provider, demo_mode=False)

    def _make_openai_client(self) -> Any:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMProviderError("ثبّت مكتبة openai من requirements.txt.") from exc
        options: dict[str, Any] = {"api_key": self._openai_key}
        base_url = os.getenv("OPENAI_BASE_URL", "").strip()
        if base_url:
            options["base_url"] = base_url
        return OpenAI(**options)

    def _make_gemini_client(self) -> Any:
        try:
            from google import genai
        except ImportError as exc:
            raise LLMProviderError("ثبّت مكتبة google-genai من requirements.txt.") from exc
        return genai.Client(api_key=self._gemini_key)

    @staticmethod
    def _usable_key(value: str) -> str:
        candidate = value.strip()
        if candidate.lower() in {
            "your_api_key_here",
            "your_gemini_api_key_here",
            "replace_me",
            "changeme",
        }:
            return ""
        return candidate

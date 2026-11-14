"""Environment-backed settings for an AI agents hub."""

from __future__ import annotations

import os
from dataclasses import dataclass

PROJECT_NAME = "Universe Center AI Agents"
VERSION = "1.0.0"


class SettingsError(ValueError):
    """Raised when required runtime configuration is missing or invalid."""


@dataclass(frozen=True, slots=True)
class Settings:
    api_key: str
    model: str
    base_url: str | None
    timeout_seconds: float
    max_output_tokens: int
    hub_api_key: str | None = None
    hub_port: int = 8000

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key or api_key.lower() in {"your_api_key_here", "replace_me", "changeme"}:
            raise SettingsError(
                "OPENAI_API_KEY غير مضبوط. أضف مفتاحك محلياً في ملف .env؛ لا ترسله في الدردشة."
            )

        model = os.getenv("DEFAULT_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o-mini")).strip()
        if not model:
            raise SettingsError("DEFAULT_MODEL لا يمكن أن يكون فارغاً.")

        try:
            timeout_seconds = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
            max_output_tokens = int(os.getenv("MAX_OUTPUT_TOKENS", "1200"))
            hub_port = int(os.getenv("HUB_PORT", "8000"))
        except ValueError as exc:
            raise SettingsError(
                "إعدادات المهلة وحد الإخراج والمنفذ يجب أن تكون أرقاماً صحيحة."
            ) from exc

        if not 1 <= timeout_seconds <= 180:
            raise SettingsError("REQUEST_TIMEOUT_SECONDS يجب أن يكون بين 1 و180.")
        if not 64 <= max_output_tokens <= 8192:
            raise SettingsError("MAX_OUTPUT_TOKENS يجب أن يكون بين 64 و8192.")
        if not 1024 <= hub_port <= 65535:
            raise SettingsError("HUB_PORT يجب أن يكون بين 1024 و65535.")

        base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
        hub_api_key = os.getenv("HUB_API_KEY", "").strip() or None
        if hub_api_key and hub_api_key.lower() in {
            "replace_with_a_long_random_token",
            "your_api_key_here",
            "changeme",
        }:
            hub_api_key = None
        if hub_api_key and len(hub_api_key) < 32:
            raise SettingsError("HUB_API_KEY يجب أن يحتوي على 32 محرفاً على الأقل.")
        return cls(
            api_key=api_key,
            model=model,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_output_tokens=max_output_tokens,
            hub_api_key=hub_api_key,
            hub_port=hub_port,
        )

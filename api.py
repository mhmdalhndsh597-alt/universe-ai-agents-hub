"""Authenticated HTTP API for human-reviewed agent drafts."""

from __future__ import annotations

import hmac
from pathlib import Path
from typing import Any, Literal

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from agents.base_agent import AgentError
from agents.content_agent import ContentAgent
from agents.support_agent import SupportAgent
from config.settings import PROJECT_NAME, VERSION, Settings, SettingsError

PROJECT_ROOT = Path(__file__).resolve().parent
MAX_BODY_BYTES = 64 * 1024


class SupportDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    message: str = Field(min_length=1, max_length=5_000)
    context: str = Field(default="", max_length=8_000)


class SummaryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    text: str = Field(min_length=1, max_length=30_000)
    max_words: int = Field(default=150, ge=20, le=2_000)
    language: str = Field(default="Arabic", min_length=1, max_length=60)


class ContentDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    brief: str = Field(min_length=1, max_length=12_000)
    format: Literal["social_post", "marketing_email", "product_description", "video_caption"] = (
        "social_post"
    )
    language: str = Field(default="Arabic", min_length=1, max_length=60)


class DraftResponse(BaseModel):
    draft: str
    requires_human_review: bool = True
    persisted: bool = False


def _settings_for(request: Request) -> Settings:
    settings = request.app.state.settings
    if settings is not None:
        return settings

    try:
        from dotenv import load_dotenv

        load_dotenv(PROJECT_ROOT / ".env", override=False)
        settings = Settings.from_env()
    except (ImportError, SettingsError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="service_not_configured",
        ) from None

    request.app.state.settings = settings
    return settings


def require_hub_auth(request: Request) -> Settings:
    settings = _settings_for(request)
    expected = settings.hub_api_key
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="api_auth_not_configured",
        )

    authorization = request.headers.get("authorization", "")
    scheme, separator, supplied = authorization.partition(" ")
    if scheme.lower() != "bearer" or not separator or not supplied.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not hmac.compare_digest(supplied.strip().encode(), expected.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return settings


def _get_agent(request: Request, settings: Settings, kind: Literal["support", "content"]) -> Any:
    state_key = f"{kind}_agent"
    agent = getattr(request.app.state, state_key)
    if agent is None:
        agent = SupportAgent(settings) if kind == "support" else ContentAgent(settings)
        setattr(request.app.state, state_key, agent)
    return agent


def _run_agent(callable_: Any) -> DraftResponse:
    try:
        return DraftResponse(draft=callable_())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    except AgentError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="model_provider_unavailable",
        ) from None


def create_app(
    settings: Settings | None = None,
    *,
    support_agent: Any | None = None,
    content_agent: Any | None = None,
) -> FastAPI:
    app = FastAPI(
        title=PROJECT_NAME,
        version=VERSION,
        description="مسودات دعم ومحتوى محمية للمراجعة البشرية؛ لا تُنفذ إجراءات تجارية.",
    )
    app.state.settings = settings
    app.state.support_agent = support_agent
    app.state.content_agent = content_agent

    @app.middleware("http")
    async def limit_request_body(request: Request, call_next: Any):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "invalid_content_length"})
            if size < 0 or size > MAX_BODY_BYTES:
                return JSONResponse(status_code=413, content={"detail": "request_too_large"})
        return await call_next(request)

    @app.get("/health", tags=["operations"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/support/draft", response_model=DraftResponse, tags=["support"])
    def support_draft(
        payload: SupportDraftRequest,
        request: Request,
        current_settings: Settings = Depends(require_hub_auth),
    ) -> DraftResponse:
        agent = _get_agent(request, current_settings, "support")
        return _run_agent(lambda: agent.draft_reply(payload.message, payload.context))

    @app.post("/v1/content/summarize", response_model=DraftResponse, tags=["content"])
    def content_summarize(
        payload: SummaryRequest,
        request: Request,
        current_settings: Settings = Depends(require_hub_auth),
    ) -> DraftResponse:
        agent = _get_agent(request, current_settings, "content")
        return _run_agent(
            lambda: agent.summarize(payload.text, payload.max_words, payload.language)
        )

    @app.post("/v1/content/draft", response_model=DraftResponse, tags=["content"])
    def content_draft(
        payload: ContentDraftRequest,
        request: Request,
        current_settings: Settings = Depends(require_hub_auth),
    ) -> DraftResponse:
        agent = _get_agent(request, current_settings, "content")
        return _run_agent(
            lambda: agent.draft(payload.brief, payload.format, payload.language)
        )

    return app


app = create_app()

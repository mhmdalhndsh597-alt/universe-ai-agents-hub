"""Command-line entry point for an AI agents hub."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from agents.base_agent import AgentError
from agents.content_agent import ContentAgent
from agents.support_agent import SupportAgent
from config.settings import Settings, SettingsError

PROJECT_ROOT = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="universe-center-ai-agents",
        description="مركز وكلاء الدعم وصناعة المحتوى — المخرجات مسودات للمراجعة البشرية.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    support = commands.add_parser("support", help="صياغة رد دعم أو مبيعات للمراجعة.")
    support.add_argument("--message", required=True, help="رسالة العميل.")
    support.add_argument("--context", default="", help="معلومات أعمال غير سرية وموثوقة.")

    summarize = commands.add_parser("summarize", help="تلخيص نص.")
    summarize.add_argument("--text", required=True, help="النص المراد تلخيصه.")
    summarize.add_argument("--max-words", type=int, default=150, help="الحد التقريبي لعدد الكلمات.")
    summarize.add_argument("--language", default="Arabic", help="لغة الملخص.")

    draft = commands.add_parser("draft", help="كتابة مسودة محتوى.")
    draft.add_argument("--brief", required=True, help="موجز الحقائق أو الفكرة.")
    draft.add_argument(
        "--format",
        dest="format_name",
        choices=("social_post", "marketing_email", "product_description", "video_caption"),
        default="social_post",
        help="شكل المسودة.",
    )
    draft.add_argument("--language", default="Arabic", help="لغة المحتوى.")

    serve = commands.add_parser("serve", help="تشغيل HTTP API على الجهاز المحلي.")
    serve.add_argument("--host", default="127.0.0.1", help="العنوان؛ الافتراضي محلي وآمن للتطوير.")
    serve.add_argument("--port", type=int, default=None, help="منفذ API؛ الافتراضي HUB_PORT أو 8000.")
    serve.add_argument("--reload", action="store_true", help="إعادة تحميل تلقائية للتطوير فقط.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        from dotenv import load_dotenv

        load_dotenv(PROJECT_ROOT / ".env", override=False)
        if args.command == "serve":
            from uvicorn import run

            port = args.port if args.port is not None else int(os.getenv("HUB_PORT", "8000"))
            if not 1024 <= port <= 65535:
                raise ValueError("المنفذ يجب أن يكون بين 1024 و65535.")
            run(
                "api:app",
                host=args.host,
                port=port,
                reload=args.reload,
                log_level="info",
            )
            return 0

        settings = Settings.from_env()

        if args.command == "support":
            result = SupportAgent(settings).draft_reply(args.message, args.context)
        elif args.command == "summarize":
            result = ContentAgent(settings).summarize(args.text, args.max_words, args.language)
        else:
            result = ContentAgent(settings).draft(args.brief, args.format_name, args.language)
        print(result)
        return 0
    except (SettingsError, AgentError, ValueError, ImportError) as exc:
        print(f"تعذر تنفيذ الطلب: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

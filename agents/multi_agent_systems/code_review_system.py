"""Bounded collaboration between a code writer and an independent reviewer."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from agents.coding.code_reviewer_agent import CodeReviewerAgent
from agents.coding.code_writer_agent import CodeWriterAgent
from config.settings import Settings
from core.llm_provider import LLMService


@dataclass(frozen=True, slots=True)
class CodeReviewOutcome:
    """Final draft and review metadata; always requires human verification."""

    code: str
    approved: bool
    review_feedback: str
    drafts_created: int
    requires_human_review: bool = True
    persisted: bool = False


class CodeReviewSystem:
    """Ask one agent to draft code and another to review it, with bounded revisions.

    The system does not execute, write to disk, commit, or deploy generated code.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        client=None,
        provider: LLMService | None = None,
        writer: CodeWriterAgent | None = None,
        reviewer: CodeReviewerAgent | None = None,
    ) -> None:
        self.writer = writer or CodeWriterAgent(settings, client=client, provider=provider)
        self.reviewer = reviewer or CodeReviewerAgent(settings, client=client, provider=provider)

    def run(
        self,
        task: str,
        *,
        max_revisions: int = 2,
        progress_callback: Callable[[str], None] | None = None,
    ) -> CodeReviewOutcome:
        if not task.strip():
            raise ValueError("وصف المهمة لا يمكن أن يكون فارغًا.")
        if len(task) > 12_000:
            raise ValueError("وصف المهمة يتجاوز الحد المسموح (12000 محرف).")
        if not isinstance(max_revisions, int) or isinstance(max_revisions, bool):
            raise ValueError("max_revisions يجب أن يكون عددًا صحيحًا.")
        if not 0 <= max_revisions <= 3:
            raise ValueError("max_revisions يجب أن يكون بين 0 و3.")

        if progress_callback:
            progress_callback("وكيل البرمجة يكتب المسودة الأولية…")
        code = self.writer.draft(task)
        drafts_created = 1
        if progress_callback:
            progress_callback("وكيل المراجعة يفحص المسودة الأولى…")
        review = self.reviewer.review(task, code)

        while not review.approved and drafts_created <= max_revisions:
            if progress_callback:
                progress_callback(f"وكيل البرمجة يعالج الملاحظات (المسودة {drafts_created + 1})…")
            code = self.writer.draft(
                task,
                previous_code=code,
                review_feedback=review.feedback,
            )
            drafts_created += 1
            if progress_callback:
                progress_callback(f"وكيل المراجعة يفحص المسودة {drafts_created}…")
            review = self.reviewer.review(task, code)

        return CodeReviewOutcome(
            code=code,
            approved=review.approved,
            review_feedback=review.feedback,
            drafts_created=drafts_created,
        )

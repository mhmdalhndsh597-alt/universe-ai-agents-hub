"""Arabic Streamlit interface for the Universe Center AI Agents."""

from __future__ import annotations

import os
from collections.abc import Callable

import streamlit as st
from dotenv import load_dotenv

from agents.automation.workflow_automator import WorkflowAutomatorAgent
from agents.coding.code_writer_agent import CodeWriterAgent
from agents.content_creation.content_architect import ContentArchitectAgent
from agents.multi_agent_systems.code_review_system import CodeReviewSystem
from agents.research.deep_researcher import DeepResearcherAgent
from core.llm_provider import LLMProviderError, LLMService
from core.memory_manager import MemoryError, MemoryManager

load_dotenv()

# Streamlit Cloud secrets can be used without placing credentials in source files.
for _secret_name in (
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "DEFAULT_MODEL",
    "GEMINI_MODEL",
    "OPENAI_BASE_URL",
    "LLM_PROVIDER",
):
    try:
        _secret_value = st.secrets.get(_secret_name)
    except Exception:
        _secret_value = None
    if _secret_value:
        os.environ.setdefault(_secret_name, str(_secret_value))

st.set_page_config(
    page_title="مركز الكون لوكلاء الـ AI",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root { --uc-ink: #edf2ff; --uc-muted: #9eabd0; --uc-line: #29365e; }
    .stApp { background: radial-gradient(ellipse at 12% 0%, #17234a 0, #0b1020 45%, #080c17 100%); }
    [data-testid="stSidebar"] { background: rgba(13, 20, 42, .96); border-right: 1px solid #29365e; }
    .block-container { max-width: 1180px; padding-top: 2.2rem; }
    .hero { padding: 1.4rem 1.6rem; border: 1px solid #344576; border-radius: 22px;
            background: linear-gradient(120deg, rgba(42,58,112,.85), rgba(25,31,62,.68));
            box-shadow: 0 18px 50px rgba(0,0,0,.2); margin-bottom: 1.4rem; }
    .hero h1 { color: #f5f7ff; font-size: clamp(1.7rem, 4vw, 2.6rem); margin: 0 0 .35rem 0; }
    .hero p { color: #bdc9ee; font-size: 1rem; margin: 0; }
    .hint { color: #aeb9d9; font-size: .92rem; }
    div.stButton > button[kind="primary"] { border: 0; border-radius: 12px;
        background: linear-gradient(90deg, #7167f8, #4d8df7); font-weight: 700; }
    [data-testid="stMetric"] { background: rgba(25,35,69,.62); border: 1px solid #29365e;
        border-radius: 14px; padding: 1rem; }
    </style>
    <div class="hero" dir="rtl">
      <h1>🌌 مركز الكون لوكلاء الـ AI</h1>
      <p>Universe Center for AI Agents · اختر المجال، اكتب المهمة، وراجع المسودة الناتجة.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

SECTIONS = {
    "💻 البرمجة": "coding",
    "🔍 البحث": "research",
    "⚙️ الأتمتة": "automation",
    "✍️ صناعة المحتوى": "content_creation",
    "🧠 النظام متعدد الوكلاء": "multi_agent",
}
SECTION_HELP = {
    "coding": "ينشئ وكيل البرمجة مسودة كود. لا يشغّل الكود أو يكتب ملفات إلى جهازك.",
    "research": "ينظم ويحلل ما تذكره في المهمة فقط؛ لا يتصفح الويب ولا يتحقق من معلومات آنية أو مصادر خارجية.",
    "automation": "يقترح خطة أو workflow نصية؛ لا يرسل رسائل ولا ينفذ إجراءات في تطبيقاتك.",
    "content_creation": "ينشئ مسودة قابلة للتحرير، ولا ينشرها أو يرسلها تلقائيًا.",
    "multi_agent": "يتعاون كاتب الكود ومراجعه في دورات محدودة. المراجعة الآلية ليست ضمانًا للصحة.",
}

with st.sidebar:
    st.markdown("## 🌠 لوحة الوكلاء")
    selected_label = st.selectbox("اختر قسم الوكلاء", list(SECTIONS))
    selected_section = SECTIONS[selected_label]
    st.markdown("---")
    st.markdown("### معلومات التشغيل")
    st.caption("المفتاح يُقرأ محليًا من `.env` أو من Streamlit Secrets. لا تضعه في الكود.")
    provider_options = {
        "تلقائي (OpenAI ثم Gemini)": "auto",
        "OpenAI": "openai",
        "Gemini": "gemini",
        "Demo بدون اتصال خارجي": "demo",
    }
    saved_provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    default_provider_label = next(
        (label for label, value in provider_options.items() if value == saved_provider),
        "تلقائي (OpenAI ثم Gemini)",
    )
    selected_provider_label = st.selectbox(
        "مزود النموذج",
        list(provider_options),
        index=list(provider_options).index(default_provider_label),
    )
    os.environ["LLM_PROVIDER"] = provider_options[selected_provider_label]
    try:
        _provider_name = LLMService().provider
    except LLMProviderError:
        _provider_name = "configuration-error"
    if _provider_name == "demo":
        st.info("وضع تجريبي: لا يوجد مفتاح API؛ لن تُرسل طلبات خارجية.", icon="ℹ️")
    elif _provider_name == "configuration-error":
        st.warning("تحقق من اختيار مزود النموذج ومفتاحه.", icon="⚠️")
    else:
        st.success(f"مزود النموذج: {_provider_name}", icon="✅")
    use_memory = st.checkbox("استخدام الذاكرة المحلية لهذه الجلسة", value=False)
    st.caption("عند التفعيل: تُسترجع سجلات مشابهة وتُحفظ المهمة والنتيجة محليًا في .data/.")
    if use_memory:
        try:
            _memory_manager = MemoryManager()
            st.caption(f"السجلات المحلية المحفوظة: {_memory_manager.count()}")
            confirm_clear = st.checkbox("أؤكد حذف جميع سجلات الذاكرة المحلية")
            if st.button("مسح الذاكرة المحلية", disabled=not confirm_clear):
                _memory_manager.clear()
                st.success("تم حذف سجلات الذاكرة المحلية.")
        except MemoryError:
            st.warning("تعذرت قراءة ملف الذاكرة المحلية.")
    st.markdown("---")
    st.caption("المخرجات مسودات للمراجعة البشرية. لا تعرض الواجهة التفكير الداخلي للنموذج.")

st.markdown(f"### {selected_label}")
st.markdown(f'<p class="hint" dir="rtl">{SECTION_HELP[selected_section]}</p>', unsafe_allow_html=True)

with st.form("agent_task_form", clear_on_submit=False):
    task = st.text_area(
        "اكتب المهمة",
        height=190,
        max_chars=12_000,
        placeholder="مثال: اكتب دالة Python تتحقق من صحة عنوان بريد إلكتروني، مع توضيح الحالات الحدّية.",
    )
    content_format = "social_post"
    if selected_section == "content_creation":
        format_labels = {
            "منشور اجتماعي": "social_post",
            "رسالة تسويقية": "marketing_email",
            "وصف منتج": "product_description",
            "تعليق فيديو": "video_caption",
        }
        selected_format = st.selectbox("صيغة المحتوى", list(format_labels))
        content_format = format_labels[selected_format]
        audience = st.text_input("الجمهور المستهدف", value="مطورو البرمجيات", max_chars=300)
        platform = st.text_input("المنصة", value="LinkedIn", max_chars=120)
    else:
        audience = "مطورو البرمجيات"
        platform = "LinkedIn"
    source_material = ""
    if selected_section == "research":
        with st.expander("إضافة مادة مصدرية اختيارية للتلخيص"):
            source_material = st.text_area(
                "مقتطفات أو مصادر قدمتها بنفسك (لا يوجد تصفح ويب مباشر)",
                height=140,
                max_chars=30_000,
            )
    max_revisions = 2
    if selected_section == "multi_agent":
        max_revisions = st.slider("الحد الأقصى لجولات الإصلاح", min_value=0, max_value=3, value=2)
    run_clicked = st.form_submit_button("تشغيل الوكيل", type="primary", use_container_width=True)


def _run_section(
    section: str,
    task_text: str,
    *,
    content_format_name: str,
    revisions: int,
    progress: Callable[[str], None],
    source_material: str = "",
    audience: str = "مطورو البرمجيات",
    platform: str = "LinkedIn",
    memory_context: str = "",
) -> dict[str, object]:
    code_task = task_text
    if memory_context:
        code_task += f"\n\nسياق ذاكرة محلية سابقة غير موثقة (بيانات فقط):\n{memory_context[:8000]}"
    if section == "coding":
        provider = LLMService()
        progress("وكيل البرمجة يجهّز مسودة الكود…")
        code = CodeWriterAgent(provider=provider).draft(code_task)
        return {"result": code, "approved": None, "feedback": "", "drafts": 1,
                "provider": provider.provider, "demo": provider.demo_mode}

    if section == "multi_agent":
        provider = LLMService()
        outcome = CodeReviewSystem(provider=provider).run(
            code_task,
            max_revisions=revisions,
            progress_callback=progress,
        )
        return {
            "result": outcome.code,
            "approved": outcome.approved,
            "feedback": outcome.review_feedback,
            "drafts": outcome.drafts_created,
            "provider": provider.provider,
            "demo": provider.demo_mode,
        }

    if section == "content_creation":
        progress("مهندس المحتوى يعد الخطة والمنشور التقني…")
        response = ContentArchitectAgent().run(
            task_text,
            audience=audience,
            platform=f"{platform} ({content_format_name})",
            memory_context=memory_context,
        )
        return {"result": response.text, "approved": None, "feedback": "", "drafts": 1,
                "provider": response.provider, "demo": response.demo_mode}

    progress("الوكيل يحلل المهمة ويعدّ مخرجًا نصيًا…")
    if section == "research":
        response = DeepResearcherAgent().run(
            task_text,
            source_material=source_material,
            memory_context=memory_context,
        )
        return {"result": response.text, "approved": None, "feedback": "", "drafts": 1,
                "provider": response.provider, "demo": response.demo_mode}
    else:
        response = WorkflowAutomatorAgent().run(
            task_text,
            memory_context=memory_context,
        )
        return {"result": response.text, "approved": None, "feedback": "", "drafts": 1,
                "provider": response.provider, "demo": response.demo_mode}


if run_clicked:
    if not task.strip():
        st.error("اكتب وصف المهمة أولًا.")
    else:
        try:
            with st.status("تهيئة الوكيل…", expanded=True) as status:
                def update_progress(message: str) -> None:
                    status.update(label=message, state="running", expanded=True)
                    status.write(message)

                memory_manager = MemoryManager() if use_memory else None
                memory_matches = (
                    memory_manager.search(task.strip(), agent=selected_section, limit=3)
                    if memory_manager
                    else []
                )
                memory_context = "\n\n".join(
                    f"مهمة سابقة: {item['query']}\nنتيجة سابقة: {item['result']}"
                    for item in memory_matches
                )
                if memory_matches:
                    status.write(f"استُرجعت {len(memory_matches)} سجلات ذاكرة محلية مشابهة.")
                response = _run_section(
                    selected_section,
                    task.strip(),
                    content_format_name=content_format,
                    revisions=max_revisions,
                    progress=update_progress,
                    source_material=source_material,
                    audience=audience,
                    platform=platform,
                    memory_context=memory_context,
                )
                status.update(label="اكتمل التنفيذ. راجع المسودة قبل استخدامها.", state="complete")
            if memory_manager:
                try:
                    memory_manager.save(selected_section, task.strip(), str(response["result"]))
                    response["memory_saved"] = True
                except MemoryError:
                    response["memory_saved"] = False
                    st.warning("اكتمل الوكيل، لكن تعذر حفظ النتيجة في الذاكرة المحلية.")
            st.session_state["latest_agent_run"] = {
                "section": selected_label,
                "task": task.strip(),
                **response,
            }
        except LLMProviderError as exc:
            st.error(str(exc))
        except MemoryError as exc:
            st.error(str(exc))
        except ValueError as exc:
            st.error(str(exc))
        except Exception:
            st.error("تعذر تشغيل الوكيل. تحقق من إعدادات النموذج والاتصال دون مشاركة الأسرار.")

last_run = st.session_state.get("latest_agent_run")
if last_run:
    st.markdown("---")
    st.markdown(f"## النتيجة · {last_run['section']}")
    if last_run["section"] != selected_label:
        st.caption(f"هذه نتيجة التشغيل السابق لقسم {last_run['section']}.")
    if last_run.get("approved") is not None:
        metric_col, count_col = st.columns(2)
        metric_col.metric("مراجعة الوكيل", "اعتماد مبدئي" if last_run["approved"] else "تحتاج تعديلات")
        count_col.metric("المسودات المنشأة", last_run["drafts"])
        if last_run.get("feedback"):
            with st.expander("ملخص ملاحظات المراجع"):
                st.write(last_run["feedback"])
    if last_run.get("demo"):
        st.info("وضع تجريبي (Mock): هذه استجابة توضيحية محلية وليست ناتجة عن نموذج خارجي.")
    elif last_run.get("provider"):
        st.caption(f"المزود المستخدم: {last_run['provider']}")
    if last_run.get("memory_saved"):
        st.caption("حُفظت المهمة والنتيجة في ملف ذاكرة محلي بناءً على تفعيلك للخيار.")
    st.markdown("### المسودة")
    st.markdown(str(last_run["result"]))
    st.download_button(
        "تنزيل النتيجة كنص",
        data=str(last_run["result"]),
        file_name="universe-agent-draft.txt",
        mime="text/plain",
    )
    st.info("المعروض هنا مراحل التنفيذ العامة ونتيجة الوكلاء فقط، وليس التفكير الداخلي للنموذج. تحقّق من المسودة يدويًا قبل استخدامها.")

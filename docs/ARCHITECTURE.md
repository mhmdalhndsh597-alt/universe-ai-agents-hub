# البنية | Architecture

## العربية

يعتمد المشروع فصلًا بسيطًا بين الواجهات والوكلاء والإعدادات:

- `main.py`: نقطة دخول CLI وتشغيل الخدمة.
- `api.py`: مسارات FastAPI والتحقق من المدخلات ومصادقة Bearer.
- `agents/base_agent.py`: عميل مشترك يرسل طلبًا واحدًا لمزود النموذج دون حفظ المحادثة.
- `agents/support_agent.py` و`agents/content_agent.py`: الوكلاء المطبقون حاليًا.
- `agents/coding/`: يتضمن وكيل صياغة الكود ووكيل مراجعته.
- `agents/multi_agent_systems/code_review_system.py`: ينسق دورة كتابة ثم مراجعة، ويعيد المسودة للمبرمج عند طلب التعديلات ضمن عدد محدود من الجولات. لا ينفذ الكود أو يحفظه أو يرفعه، والاعتماد الآلي لا يغني عن المراجعة البشرية.
- `agents/research/deep_researcher.py`: يجزئ الموضوع إلى أسئلة ويلخص المادة المقدمة؛ لا يتصفح الويب.
- `agents/automation/workflow_automator.py`: ينتج خطة workflow ولا ينفذ إجراء خارجي.
- `agents/content_creation/content_architect.py`: ينشئ خطة محتوى ومسودة منشور تقني.
- `core/llm_provider.py`: موائم OpenAI/Gemini مع اختيار تلقائي ووضع Demo عند عدم وجود مفاتيح.
- `core/memory_manager.py`: مخزن متجهات JSON محلي باستخدام ميزات token hashing، دون embeddings خارجية. تشغيله في الواجهة اختياري بموافقة المستخدم، والملف غير مشفر ومستبعد من Git.
- `app.py`: واجهة Streamlit عربية تُظهر مراحل التنفيذ العامة فقط، لا التفكير الداخلي.
- `templates/`: قالب بداية لإضافة وكيل جديد.

لا توجد جدولة أو تكاملات مراسلة افتراضيًا. لا يستخدم وضع Demo مزودًا خارجيًا، وتظل مخرجاته أمثلة توضيحية. الذاكرة لا تحفظ تلقائيًا؛ فعّلها من الواجهة بعد مراجعة تحذير الخصوصية، ولا تخزن بيانات حساسة. عند إتاحة API خارج الجهاز المحلي، راجع TLS، تحديد معدل الطلبات، تدوير الأسرار، والمصادقة المناسبة لعدد المستخدمين.

## English

The project provides a Streamlit UI, CLI, and optional FastAPI API. The new research, workflow-planning, and content agents use the shared OpenAI/Gemini adapter and fall back to clearly labeled local demo outputs when credentials are absent. Research does not browse the web, and automation only drafts plans. The code-review team uses bounded revisions and never executes or persists generated source. `MemoryManager` stores opt-in records in a local JSON hashed-token vector store (not semantic embeddings); the file is unencrypted and ignored by Git. The UI exposes general progress, not private chain-of-thought. Public API deployments require HTTPS, rate limiting, secret rotation, and appropriate authentication.

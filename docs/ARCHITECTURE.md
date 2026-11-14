# البنية | Architecture

## العربية

يعتمد المشروع فصلًا بسيطًا بين الواجهات والوكلاء والإعدادات:

- `main.py`: نقطة دخول CLI وتشغيل الخدمة.
- `api.py`: مسارات FastAPI والتحقق من المدخلات ومصادقة Bearer.
- `agents/base_agent.py`: عميل مشترك يرسل طلبًا واحدًا لمزود النموذج دون حفظ المحادثة.
- `agents/support_agent.py` و`agents/content_agent.py`: الوكلاء المطبقون حاليًا.
- `agents/coding/`, `research/`, `automation/`, `content_creation/`, `multi_agent_systems/`: تصنيفات للتوسعة، وليست ادعاءً بأن وكلاء كل مجال جاهزون.
- `core/`: مكان مقترح لمكونات مشتركة مستقبلية، مثل واجهات أدوات مجردة؛ لا توجد ذاكرة دائمة مفعّلة حاليًا.
- `templates/`: قالب بداية لإضافة وكيل جديد.

لا توجد قاعدة بيانات أو جدولة أو تكاملات مراسلة افتراضيًا. أضف هذه القدرات فقط مع إعدادات واضحة واختبارات وتوثيق للاحتفاظ بالبيانات والصلاحيات. عند إتاحة API خارج الجهاز المحلي، راجع TLS، تحديد معدل الطلبات، تدوير الأسرار، والمصادقة المناسبة لعدد المستخدمين.

## English

The project separates interfaces, agents, and settings. `main.py` provides the CLI/server entry point; `api.py` provides validated, Bearer-protected FastAPI routes; `agents/base_agent.py` shares the provider client; and the support/content agents are currently implemented. The category folders are extension points, not claims of completed agents. `core/` and `templates/` are reserved for shared components and starter patterns. No database, scheduler, messaging integration, or persistent memory is enabled. Public deployments require HTTPS, rate limiting, secret rotation, and appropriate authentication.

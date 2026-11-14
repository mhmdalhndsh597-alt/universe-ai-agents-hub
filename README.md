<div align="center">

# 🌌 مركز الكون لوكلاء الـ AI
### Universe Center for AI Agents

**مركز مفتوح وقابل للتوسّع لتنظيم وكلاء الذكاء الاصطناعي وتطويرهم — مع توضيح ما هو منفّذ وما يزال ضمن خطة التطوير.**

[أقسام الوكلاء](#-أقسام-الوكلاء-agents-categories) • [البدء السريع](#-البدء-السريع) • [المساهمة](#-كيف-تساهم-في-المشروع-contributing) • [خارطة الطريق](#-خارطة-الطريق-roadmap)

</div>

---

## 🚀 عن المشروع | About

يهدف **مركز الكون لوكلاء الـ AI** إلى توفير بنية Python منظمة وقابلة للتوسّع لبناء وكلاء الذكاء الاصطناعي، مع واجهة سطر أوامر وواجهة FastAPI اختيارية. يتضمن هذا الإصدار وكلاء دعم ومحتوى كبداية عملية، ومجلدات تصنيف لإضافة قدرات جديدة.

> **شفافية النطاق:** المشروع لا يدّعي أنه أكبر مستودع، ولا أن جميع أنواع الوكلاء جاهزة. تكامل WhatsApp وTelegram والبريد وCRM، وذاكرة المحادثة، والأتمتة الخارجية، ولوحة التحكم ليست مفعّلة في الإصدار الحالي. كل ناتج مسودة تحتاج مراجعة بشرية. تُرسل المدخلات إلى مزود النموذج الذي تضبطه؛ لا ترسل بيانات حساسة.

## 🤖 أقسام الوكلاء | Agents Categories

| القسم | نطاقه المقترح | أمثلة مستقبلية غير منفذة بعد |
|---|---|---|
| `agents/coding/` | البرمجة ومراجعة الأكواد | CodeReviewer، BugHunter، RepoBuilder |
| `agents/research/` | البحث وتحليل البيانات | DeepSearcher، MarketAnalyst، PDFReader |
| `agents/automation/` | تصميم workflows والأتمتة | EmailAssistant، WorkflowManager |
| `agents/content_creation/` | صناعة المحتوى والتسويق | مسودات حملات وأوصاف منتجات |
| `agents/multi_agent_systems/` | تنسيق تعاون عدة وكلاء | فرق وكلاء لمهام متعددة الخطوات |

الوكلاء المنفذون حاليًا في جذر `agents/` هم وكيل الدعم (`support_agent.py`) ووكيل المحتوى (`content_agent.py`). تصنيفات المجلدات أعلاه نقاط توسعة فقط.

## ⚡ البدء السريع

يتطلب Python 3.10 أو أحدث:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cp .env.example .env
```

أضف إعدادات مزود النموذج إلى `.env` محليًا. لتشغيل API، أنشئ `HUB_API_KEY` قويًا محليًا، مثل:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

لا ترفع `.env` أو المفاتيح السرية إلى Git. استخدم CLI:

```bash
python main.py --help
python main.py support --message "ما تفاصيل الخدمة؟" --context "السعر يحدد بعد المعاينة"
python main.py summarize --text "النص المراد تلخيصه" --max-words 120 --language Arabic
python main.py draft --brief "إعلان عن خدمة" --format social_post --language Arabic
```

لتشغيل الواجهة محليًا: `python main.py serve`. افتراضيًا تستمع إلى `127.0.0.1`؛ وتتوفر وثائق API عادة على `http://127.0.0.1:8000/docs`. مسارات العمل محمية بمفتاح Bearer. لا تعرض الخدمة للإنترنت دون TLS ومحدد معدل طلبات ومراجعة أمنية ومصادقة ملائمة.

## 🧱 بنية المشروع

```text
agents/                  الوكلاء وتصنيفات المجالات
  coding/                نقطة توسعة لوكلاء البرمجة
  research/              نقطة توسعة للبحث والتحليل
  automation/            نقطة توسعة لتصميم workflows
  content_creation/      نقطة توسعة لصناعة المحتوى
  multi_agent_systems/   نقطة توسعة لتنسيق الوكلاء
core/                    مساحة للمكونات المشتركة المستقبلية
config/                  إعدادات البيئة
api.py                   واجهة FastAPI والتحقق والمصادقة
main.py                  CLI وتشغيل الخدمة
templates/               قالب إضافة وكيل
docs/                    وثائق المشروع
 tests/                  اختبارات تستخدم مكونات وهمية
```

راجع [دليل البنية](docs/ARCHITECTURE.md) و[دليل المساهمة](CONTRIBUTING.md). قالب الوكيل متاح في `templates/agent_skeleton.py`.

## 🧪 الاختبارات والجودة

```bash
python -m pip install -r requirements-dev.txt
ruff check .
python -m compileall -q main.py api.py agents config core tests templates
pytest -q
```

تستخدم اختبارات الوحدة عملاء وهميين ولا تتطلب مفتاحًا أو اتصالًا بمزود خارجي.

## 🤝 كيف تساهم في المشروع | Contributing

نرحب بالمساهمات. أنشئ فرعًا للتغيير، وضع الوكيل في التصنيف المناسب، وأضف اختبارات ووثائق توضّح نطاقه وحدوده. أعد استخدام العميل المشترك، ولا تضع أسرارًا أو بيانات حقيقية في الكود أو الاختبارات. تُرسل المساهمات إلى المستودع بعد نشر رابطه الرسمي؛ لم يُحدد رابط مستودع عام لهذا المشروع بعد.

## 🗺️ خارطة الطريق | Roadmap

- [x] إنشاء نقطة بداية Python مع CLI وواجهة API اختيارية محمية.
- [x] إضافة تصنيفات الوكلاء وقالب توسيع ووثائق مساهمة.
- [ ] تنفيذ وكلاء إضافيين واختبارات لكل مجال.
- [ ] تقييم جدوى لوحة تحكم مرئية لإدارة التشغيل.
- [ ] دراسة تكاملات أطر الوكلاء ومزودي النماذج، كلٌ على حدة وباختبارات موثقة.

كل البنود غير المكتملة أهداف مستقبلية وليست ميزات متاحة حاليًا.

---

<div align="center">بُني ليكون نقطة انطلاق واضحة وآمنة لمجتمع المطورين.</div>

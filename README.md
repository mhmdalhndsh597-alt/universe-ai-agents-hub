# 🌌 مركز الكون لوكلاء الـ AI (Universe Center for AI Agents)

<p align="center">
  <strong>منصة عامة قيد البناء لتجميع وكلاء الذكاء الاصطناعي، وتسهيل اكتشافهم وتشغيلهم وربطهم بالتطبيقات.</strong>
</p>

<p align="center">
  <img alt="Python 3.12+" src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white">
  <img alt="Streamlit" src="https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit&logoColor=white">
  <img alt="Security-first" src="https://img.shields.io/badge/Security-fail--closed-2E7D32?logo=github">
  <img alt="Status" src="https://img.shields.io/badge/Status-Active%20Development-orange">
</p>

**الحالة / Status:** تطوير نشط — النسخة العامة قيد الإعداد، والنسخة الخاصة الحالية مرحلية. الخصائص أدناه ضمن نطاق البناء، وليست ادعاءً بأن كل تكامل أو تشغيل إنتاجي متاح الآن. لا تُخزّن مفاتيح أو أسرار في Git، والتنفيذ الخارجي معطّل افتراضيًا. لم يُعتمد ترخيص بعد؛ الإتاحة العامة للاطلاع لا تمنح تلقائيًا حقوق إعادة الاستخدام أو إعادة التوزيع.

---

## العربية

### الرؤية

يهدف **مركز الكون لوكلاء الـAI** إلى بناء منصة عامة تجمع وكلاء الذكاء الاصطناعي في مكان واحد، وتساعد المطورين على اكتشافهم وتقييمهم وربطهم بأمان. سيُختار ترخيص مفتوح مناسب قبل دعوة المجتمع لإعادة الاستخدام أو إعادة التوزيع. تشمل فئات المنصة المستهدفة البرمجة، والبحث، والأتمتة، وصناعة المحتوى، والأنظمة متعددة الوكلاء.

### المميزات الرئيسية (Key Features)

- **تعدد النماذج:** تصميم موحد للتبديل بين Google Gemini وOpenAI وAnthropic Claude ونماذج Ollama المحلية المجانية. عند غياب بيانات الاعتماد، يكون وضع العرض التجريبي هو الافتراضي؛ لا تُضمّن المفاتيح في الشيفرة.
- **أدوات عملية بضوابط واضحة:** بحث الويب، وتحليل الملفات النصية والبرمجية وPDF، وتنفيذ Python داخل Docker rootless معزول فقط، وقراءة Issues وPull Requests من GitHub. الأدوات غير مفعّلة افتراضيًا، والمنفذ يرفض التنفيذ إذا لم تتوفر بيئة العزل المطلوبة.
- **واجهة API موحدة:** FastAPI مع توثيق Swagger UI تلقائي على `/docs` لربط التطبيقات الخارجية، مع حماية نقاط التشغيل بمفتاح API عند استخدام مزود أو أداة.
- **لوحة تحكم تفاعلية:** واجهة Streamlit لاكتشاف الوكلاء والبحث والتصفية واختيار المزود والأدوات وتوليد أمثلة Python وcURL.
- **حوكمة وأمان:** أقل صلاحية، موافقة بشرية على التغييرات، حفظ مفاتيح الخدمات في GitHub Secrets أو متغيرات البيئة المحمية، وفحوص آلية قبل الدمج.

### اقتصاد المطورين وتقاسم الأرباح (Developer Marketplace & 80/20 Revenue Share)

نستهدف سوقًا يسمح للمطورين بتقديم وكلائهم للمراجعة والنشر، مع **نموذج تقاسم مقترح** يخصص 80% من عوائد الاستخدام المنسوبة إلى الوكيل للمطور و20% للمنصة. تفاصيل الأهلية والقياس والتسوية موضحة في [مسودة اتفاقية المطورين](DEVELOPER_AGREEMENT.md).

> **تنويه مهم:** نسبة 80/20 سياسة مقترحة للمراجعة وليست حاليًا وعدًا بالدفع أو خدمة تسوية مفعّلة. لا توجد في هذه النسخة منظومة مكتملة لقياس الاستخدام أو الفوترة أو تحويل الأرباح. لن يصبح البرنامج نافذًا إلا بعد اعتماد الاتفاقية وتفعيل نظام القياس والتحصيل وإجراءات الامتثال ذات الصلة.

### البدء السريع (Quick Start)

يتطلب Python 3.12 أو أحدث. أنشئ بيئة افتراضية ثم ثبّت المتطلبات:

```bash
git clone https://github.com/mhmdalhndsh597-alt/universe-ai-agents-hub-public.git
cd universe-ai-agents-hub
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

انسخ `.env.example` إلى `.env` عند الحاجة، وأضف مفاتيحك محليًا أو في GitHub Secrets فقط. لا ترفع `.env` إلى Git. ابدأ خادم API والواجهة في نافذتين منفصلتين:

```bash
uvicorn api_server:app --host 127.0.0.1 --port 8000
```

```bash
streamlit run app.py
```

بعد التشغيل، افتح لوحة Streamlit محليًا، وتوثيق API التفاعلي على `http://127.0.0.1:8000/docs`. إذا لم تُضبط مفاتيح مزود النماذج، استخدم Demo Mode. لا تعرّض الخادم للإنترنت مباشرة قبل ضبط `HUB_API_KEY` ومراجعة إعدادات النشر والحماية.

### المساهمة في المشروع (Contributing)

نرحب بمساهمات مطوري العالم في الشيفرة والتوثيق والاختبارات. ابدأ بقراءة [دليل المساهمة](CONTRIBUTING.md)، وافتح Issue أو Pull Request موضحًا نطاق التغيير واختباراته. تُراجع التغييرات قبل دمجها، ولا تُشارك الأسرار أو بيانات الاعتماد في Issues أو Pull Requests.

### الأمان

اقرأ [سياسة الأمان](SECURITY.md) و[نموذج التهديد](docs/security-model.md). المستودع العام لا ينبغي أن يحتوي أسرارًا مطلقًا؛ أما إعدادات النشر الخاصة فتُحفظ في GitHub Secrets/Environments، وليس في ملفات المستودع الخاص.

---

## English

### Vision

**Universe Center for AI Agents** aims to become a public hub for discovering, evaluating, and safely connecting AI agents. An open-source license will be selected before third-party reuse or redistribution is invited. Target categories include software development, research, automation, content creation, and multi-agent systems.

### Key Features

- **Multi-provider architecture:** a common interface for Google Gemini, OpenAI, Anthropic Claude, and free local models through Ollama. Demo mode is the safe fallback when credentials are absent; API keys never belong in source files.
- **Practical tools with guardrails:** web search, text/code/PDF analysis, Python execution only inside an isolated rootless Docker container, and read-only GitHub Issues/Pull Requests access. Tools are off by default; code execution fails closed if the required sandbox is unavailable.
- **Unified API:** FastAPI with automatic Swagger UI at `/docs` for external integrations. Run endpoints require an API key when a real provider or tool is used.
- **Interactive dashboard:** a Streamlit UI for agent discovery, search and category filters, provider/tool selection, and Python/cURL integration snippets.
- **Governance and security:** least privilege, human review for changes, credentials stored in protected environment variables or GitHub Secrets, and automated checks before merge.

### Developer Marketplace & 80/20 Revenue Share

The planned marketplace is intended to let developers submit agents for review and publication. The proposed model allocates **80% of eligible usage revenue attributable to an agent to its developer and 20% to the platform**. See the [Draft Developer Agreement](DEVELOPER_AGREEMENT.md) for proposed terms.

> **Important:** the 80/20 split is a proposal for review, not an active payment promise or payout service. Usage metering, billing, settlement, and related compliance workflows are not complete in this version. The program will not become effective until the agreement is approved and the required systems are operational.

### Quick Start

Requires Python 3.12 or newer:

```bash
git clone https://github.com/mhmdalhndsh597-alt/universe-ai-agents-hub-public.git
cd universe-ai-agents-hub
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy `.env.example` to `.env` if needed and provide credentials locally or through GitHub Secrets only. Never commit `.env`. Start the API and dashboard in separate terminals:

```bash
uvicorn api_server:app --host 127.0.0.1 --port 8000
streamlit run app.py
```

Open the Streamlit URL printed by the CLI and visit `http://127.0.0.1:8000/docs` for Swagger UI. Demo Mode is used when provider credentials are missing. Do not expose the server publicly until `HUB_API_KEY`, deployment controls, and access restrictions are configured.

### Contributing

Developers worldwide can review the project and propose improvements to code, documentation, and tests. Please read [CONTRIBUTING.md](CONTRIBUTING.md), then open an Issue or Pull Request with a clear scope and test results. Changes require review; never place credentials or secrets in Issues or Pull Requests. The repository license is still to be selected; public visibility alone does not grant reuse rights.

### Security

See [SECURITY.md](SECURITY.md) and the [security model](docs/security-model.md). Public source must never contain secrets. Private deployment settings belong in protected GitHub Secrets/Environments—not in tracked files, even in a private repository.

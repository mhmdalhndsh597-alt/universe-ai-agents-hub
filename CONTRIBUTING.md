# المساهمة | Contributing

نرحب بمساهمات المجتمع في الشيفرة والتوثيق والاختبارات. افتح Issue يوضح الهدف والنطاق قبل إضافة تكامل أو قدرة جديدة، واجعل التغيير محدودًا وقابلًا للمراجعة. لا تفعّل تنفيذ الوكلاء أو توسّع صلاحياتهم ضمنيًا.

قبل إرسال Pull Request:

1. ضع الوكيل في القسم المناسب، وحدد مسؤوليته وحدود سلوكه.
2. لا تضف أسرارًا أو مفاتيح أو بيانات مستخدمين إلى Git أو سجلات CI أو نصوص Issues/PR.
3. أضف اختبارات للتغييرات، واستخدم عملاء وهميين بدل استدعاء مزودي النماذج في اختبارات الوحدة.
4. وضّح وضع Demo، والخصوصية، وأي تخزين أو اتصال خارجي جديد.
5. شغّل الفحوص محليًا:

   ```bash
   python -m unittest discover -s tests -v
   python -m ai_agents_hub validate
   ruff check .
   pytest -q
   ```

6. قدّم Pull Request للمراجعة البشرية مع نطاق التغيير ونتائج الاختبار. الدمج أو نجاح CI لا يعني موافقة على تغيير أمني عالي الأثر.

## English

Contributions to code, documentation, and tests are welcome. Open an Issue to define the scope before adding integrations or capabilities. Keep changes small and reviewable; do not implicitly enable agent execution or broaden permissions.

Before submitting a Pull Request, place agents in the appropriate category, document their scope, never commit secrets or user data, add deterministic tests with mocked providers, and describe Demo behavior, privacy, storage, and external connections. Run the test and lint commands above. All changes require human review; successful CI is not approval for high-impact security changes.

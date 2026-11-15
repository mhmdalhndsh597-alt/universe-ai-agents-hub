from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


class StreamlitAppTests(unittest.TestCase):
    def test_all_sections_render_demo_results(self) -> None:
        sections = [
            "💻 البرمجة",
            "🔍 البحث",
            "⚙️ الأتمتة",
            "✍️ صناعة المحتوى",
            "🧠 النظام متعدد الوكلاء",
        ]
        clean_environment = {
            "LLM_PROVIDER": "demo",
            "OPENAI_API_KEY": "",
            "GEMINI_API_KEY": "",
            "GOOGLE_API_KEY": "",
        }
        with patch.dict(os.environ, clean_environment, clear=False):
            for section in sections:
                with self.subTest(section=section):
                    app = AppTest.from_file(
                        Path(__file__).resolve().parents[1] / "app.py",
                        default_timeout=20,
                    ).run()
                    self.assertFalse([item.message for item in app.exception])
                    app.selectbox[0].select(section)
                    app.text_area[0].set_value("مهمة اختبارية: تحليل موضوع API")
                    app.form_submit_button[0].click().run()

                    self.assertFalse([item.message for item in app.exception])
                    self.assertFalse([item.value for item in app.error])
                    self.assertTrue(
                        any("النتيجة" in (item.value or "") for item in app.markdown)
                    )
                    self.assertTrue(
                        any("وضع تجريبي" in (item.value or "") for item in app.info)
                    )


if __name__ == "__main__":
    unittest.main()

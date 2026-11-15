from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.memory_manager import MemoryManager


class MemoryManagerTests(unittest.TestCase):
    def test_persists_and_searches_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            memory = MemoryManager(Path(directory) / "memory.json")
            memory.save("research", "تحليل واجهات برمجة التطبيقات", "ملاحظات عن API")
            memory.save("automation", "تنظيم جدول أسبوعي", "خطة أسبوعية")

            matches = memory.search("واجهات برمجة التطبيقات", agent="research")

            self.assertEqual(memory.count(), 2)
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]["agent"], "research")
            self.assertGreater(matches[0]["similarity"], 0)
            self.assertTrue(Path(directory, "memory.json").exists())

    def test_empty_query_returns_no_matches(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            memory = MemoryManager(Path(directory) / "memory.json")
            memory.save("content", "منشور تقني", "مسودة")
            self.assertEqual(memory.search("   "), [])

    def test_rejects_oversized_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            memory = MemoryManager(Path(directory) / "memory.json")
            with self.assertRaises(ValueError):
                memory.save("research", "x" * 12_001, "result")

    def test_clear_deletes_all_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            memory = MemoryManager(Path(directory) / "memory.json")
            memory.save("research", "topic alpha", "result beta")
            memory.clear()
            self.assertEqual(memory.count(), 0)


if __name__ == "__main__":
    unittest.main()

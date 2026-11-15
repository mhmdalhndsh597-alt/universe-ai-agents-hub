"""Local JSON memory with lightweight lexical similarity and atomic writes."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class MemoryError(RuntimeError):
    """Safe local-memory read/write error."""


class MemoryManager:
    """Persist user-approved runs and retrieve by deterministic hashed-token vectors.

    This is a lightweight local JSON vector store without model-generated embeddings.
    The caller is responsible for obtaining consent before saving sensitive content.
    """

    _lock = threading.RLock()

    def __init__(self, path: str | Path | None = None, *, max_records: int = 2000) -> None:
        if not 1 <= max_records <= 20_000:
            raise ValueError("max_records must be between 1 and 20000.")
        configured_path = path or os.getenv("AGENT_MEMORY_PATH", ".data/agent_memory.json")
        self.path = Path(configured_path).expanduser().resolve()
        self.max_records = max_records

    def save(self, agent: str, query: str, result: str) -> dict[str, str]:
        agent = agent.strip()
        query = query.strip()
        result = result.strip()
        if not agent or not query or not result:
            raise ValueError("agent وquery وresult لا يمكن أن تكون فارغة.")
        if len(agent) > 120 or len(query) > 12_000 or len(result) > 50_000:
            raise ValueError("تجاوز سجل الذاكرة حد الطول المسموح.")

        record = {
            "id": uuid.uuid4().hex,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "agent": agent,
            "query": query,
            "result": result,
            "vector": self._vectorize(f"{query} {result}"),
        }
        with self._lock:
            records = self._read_records()
            records.append(record)
            self._write_records(records[-self.max_records :])
        return {"id": record["id"], "created_at": record["created_at"]}

    def search(self, query: str, *, agent: str | None = None, limit: int = 5) -> list[dict[str, Any]]:
        query_vector = self._vectorize(query)
        if not any(query_vector) or limit <= 0:
            return []
        if limit > 50:
            raise ValueError("limit must not exceed 50.")

        with self._lock:
            records = self._read_records()
        matches: list[tuple[float, int, dict[str, Any]]] = []
        for index, record in enumerate(records):
            if agent and record.get("agent") != agent:
                continue
            record_vector = record.get("vector") or self._vectorize(
                f"{record.get('query', '')} {record.get('result', '')}"
            )
            score = self._cosine(query_vector, record_vector)
            if score > 0:
                matches.append((score, index, record))
        matches.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [
            {**record, "similarity": round(score, 4)}
            for score, _index, record in matches[:limit]
        ]

    def count(self) -> int:
        with self._lock:
            return len(self._read_records())

    def clear(self) -> None:
        """Delete all local memory records; callers should make this user-initiated."""
        with self._lock:
            self._write_records([])

    def _read_records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raise MemoryError("تعذر قراءة ملف الذاكرة المحلية؛ لم يتم تعديله.") from None
        if not isinstance(data, list) or any(not isinstance(item, dict) for item in data):
            raise MemoryError("تنسيق ملف الذاكرة المحلية غير صالح.")
        return data

    def _write_records(self, records: list[dict[str, Any]]) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{self.path.name}.", suffix=".tmp", dir=self.path.parent
            )
            try:
                with os.fdopen(descriptor, "w", encoding="utf-8") as temporary_file:
                    json.dump(records, temporary_file, ensure_ascii=False, indent=2)
                    temporary_file.flush()
                    os.fsync(temporary_file.fileno())
                os.chmod(temporary_name, 0o600)
                os.replace(temporary_name, self.path)
                try:
                    os.chmod(self.path, 0o600)
                except OSError:
                    pass
            finally:
                if os.path.exists(temporary_name):
                    os.unlink(temporary_name)
        except OSError:
            raise MemoryError("تعذر حفظ ملف الذاكرة المحلية.") from None

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {token.casefold() for token in re.findall(r"[\w]{2,}", text, flags=re.UNICODE)}

    @classmethod
    def _vectorize(cls, text: str, dimensions: int = 256) -> list[float]:
        vector = [0.0] * dimensions
        for token in cls._tokens(text):
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "big") % dimensions
            vector[index] += 1.0 if digest[4] & 1 else -1.0
        return vector

    @staticmethod
    def _cosine(left: list[float], right: list[float]) -> float:
        dot = sum(a * b for a, b in zip(left, right, strict=False))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        if not left_norm or not right_norm:
            return 0.0
        return max(0.0, dot / (left_norm * right_norm))

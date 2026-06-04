from datetime import datetime
from typing import Any, Optional

class MemoryStore:
    """Shared memory for all agents. One instance. Everyone reads and writes here."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._short_term: dict = {}
        self._long_term: list = []
        self._initialized = True
        print("[Memory] MemoryStore initialized")

    def write(self, key: str, value: Any, long_term: bool = False):
        self._short_term[key] = {"value": value, "timestamp": datetime.now().isoformat()}
        if long_term:
            words = set(str(value).lower().split())
            for entry in self._long_term:
                if entry["key"] == key:
                    entry["value"] = str(value)
                    entry["words"] = words
                    print(f"[Memory] Updated long-term: {key}")
                    return
            self._long_term.append({"key": key, "value": str(value), "words": words})
        print(f"[Memory] Wrote: {key}")

    def read(self, key: str) -> Optional[Any]:
        entry = self._short_term.get(key)
        return entry["value"] if entry else None

    def search(self, query: str, top_k: int = 3) -> list:
        query_words = set(query.lower().split())
        scored = []
        for entry in self._long_term:
            overlap = len(query_words & entry["words"])
            if overlap > 0:
                scored.append((overlap, entry["value"]))
        for key, entry in self._short_term.items():
            val_words = set(str(entry["value"]).lower().split())
            overlap = len(query_words & val_words)
            if overlap > 0:
                scored.append((overlap, str(entry["value"])))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [v for _, v in scored[:top_k]]

    def get_all(self) -> dict:
        return {k: v["value"] for k, v in self._short_term.items()}

    def clear_short_term(self):
        self._short_term = {}
        print("[Memory] Short term memory cleared")

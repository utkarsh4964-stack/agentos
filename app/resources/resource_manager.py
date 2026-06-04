from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict

COST_PER_TOKEN = 0.000001  # Gemini free tier estimate
MAX_CALLS_PER_MINUTE = 10

class ResourceManager:
    """Tracks API usage, costs, and rate limits across all agents."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._usage: Dict[str, dict] = defaultdict(lambda: {
            "calls": 0,
            "tokens": 0,
            "cost": 0.0,
            "call_times": []
        })
        self._total_calls = 0
        self._total_tokens = 0
        self._initialized = True
        print("[ResourceManager] Initialized")

    def log_call(self, agent_name: str, tokens_used: int = 500):
        """Log an API call for an agent."""
        now = datetime.now()
        usage = self._usage[agent_name]
        usage["calls"] += 1
        usage["tokens"] += tokens_used
        usage["cost"] += tokens_used * COST_PER_TOKEN
        usage["call_times"].append(now)
        self._total_calls += 1
        self._total_tokens += tokens_used

    def check_rate_limit(self, agent_name: str) -> bool:
        """Returns True if agent is within rate limit."""
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        recent = [t for t in self._usage[agent_name]["call_times"]
                  if t > one_minute_ago]
        self._usage[agent_name]["call_times"] = recent
        return len(recent) < MAX_CALLS_PER_MINUTE

    def get_usage(self, agent_name: str) -> dict:
        """Get usage stats for a specific agent."""
        u = self._usage[agent_name]
        return {
            "agent": agent_name,
            "calls": u["calls"],
            "tokens": u["tokens"],
            "cost_usd": round(u["cost"], 6)
        }

    def get_total_cost(self) -> dict:
        """Get total usage across all agents."""
        total_cost = sum(u["cost"] for u in self._usage.values())
        return {
            "total_calls": self._total_calls,
            "total_tokens": self._total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "agents": {name: self.get_usage(name) for name in self._usage}
        }

    def check_budget(self, limit: float = 1.0) -> bool:
        """Returns True if under budget."""
        total = sum(u["cost"] for u in self._usage.values())
        if total > limit:
            print(f"[ResourceManager] ⚠️  BUDGET EXCEEDED: ${total:.4f} > ${limit}")
            return False
        return True

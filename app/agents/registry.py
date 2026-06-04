from typing import Dict, Optional, List
from app.agents.base import BaseAgent

class AgentRegistry:
    """The phonebook. Every agent registers here. Anyone can find anyone."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._agents: Dict[str, BaseAgent] = {}
        self._initialized = True
        self._register_default_agents()
        print("[Registry] AgentRegistry initialized")

    def _register_default_agents(self):
        """Pre-register the 5 core AgentOS agents."""
        defaults = [
            BaseAgent("PlannerAgent",     "Break any goal into clear, numbered subtasks",
                      "Create actionable step-by-step plans"),
            BaseAgent("ResearchAgent",    "Search and find key facts, data, and insights",
                      "Gather accurate information on any topic"),
            BaseAgent("WriterAgent",      "Write clearly and compellingly from given facts",
                      "Produce well-structured written content"),
            BaseAgent("FactCheckerAgent", "Verify and validate claims for accuracy",
                      "Ensure all information is correct and trustworthy"),
            BaseAgent("EditorAgent",      "Polish and improve written content",
                      "Make content clear, engaging, and professional"),
        ]
        for agent in defaults:
            self.register(agent)

    def register(self, agent: BaseAgent):
        """Add an agent to the registry."""
        self._agents[agent.name] = agent
        print(f"[Registry] Registered: {agent.name}")

    def get(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self._agents.get(name)

    def list_all(self) -> List[str]:
        """Return names of all registered agents."""
        return list(self._agents.keys())

    def list_all_agents(self) -> List[BaseAgent]:
        """Return all agent objects."""
        return list(self._agents.values())

    def find_best_agent(self, task: str) -> BaseAgent:
        """Find the most suitable agent for a task based on keywords."""
        task_lower = task.lower()
        rules = [
            (["plan", "break", "steps", "subtask", "organize"], "PlannerAgent"),
            (["research", "find", "search", "facts", "data", "information"], "ResearchAgent"),
            (["write", "draft", "create", "compose", "paragraph", "essay"], "WriterAgent"),
            (["verify", "check", "fact", "validate", "accurate", "true"], "FactCheckerAgent"),
            (["edit", "polish", "improve", "refine", "review", "proofread"], "EditorAgent"),
        ]
        for keywords, agent_name in rules:
            if any(kw in task_lower for kw in keywords):
                agent = self._agents.get(agent_name)
                if agent:
                    return agent
        # Default to ResearchAgent
        return self._agents.get("ResearchAgent")

    def get_all_status(self) -> List[dict]:
        """Get status of all agents."""
        return [a.to_dict() for a in self._agents.values()]

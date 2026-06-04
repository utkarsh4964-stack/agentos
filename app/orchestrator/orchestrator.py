import uuid
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    FAILED = "FAILED"

@dataclass
class SubTask:
    id: str
    description: str
    assigned_to: str
    status: TaskStatus = TaskStatus.PENDING
    result: str = ""
    depends_on: Optional[str] = None
    started_at: str = ""
    completed_at: str = ""

@dataclass
class Task:
    id: str
    goal: str
    subtasks: List[SubTask] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    final_result: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: str = ""

class Orchestrator:
    """The manager. Takes one goal. Breaks it down. Assigns it. Gets it done."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._tasks: Dict[str, Task] = {}
        self._live_updates = []
        self._initialized = True
        print("[Orchestrator] Initialized")

    def _emit(self, message: str):
        """Emit a live update for the dashboard."""
        update = {"time": datetime.now().isoformat(), "message": message}
        self._live_updates.append(update)
        print(f"[Orchestrator] {message}")

    def plan(self, goal: str) -> List[SubTask]:
        """Use PlannerAgent to break goal into subtasks, then assign agents."""
        from app.agents.registry import AgentRegistry
        registry = AgentRegistry()

        self._emit(f"Planning: {goal}")
        planner = registry.get("PlannerAgent")
        plan_text = planner.run(f"Break this goal into exactly 4 numbered steps: {goal}")

        # Parse the plan into subtasks
        subtasks = []
        lines = [l.strip() for l in plan_text.split("\n") if l.strip()]
        steps = [l for l in lines if l and (l[0].isdigit() or l.startswith("-"))]

        if len(steps) < 2:
            # Fallback: create default pipeline
            steps = [
                "1. Research the topic and gather key facts",
                "2. Write a comprehensive draft",
                "3. Fact-check all claims",
                "4. Edit and polish the final output"
            ]

        agent_sequence = ["ResearchAgent", "WriterAgent", "FactCheckerAgent", "EditorAgent"]

        prev_id = None
        for i, step in enumerate(steps[:4]):
            step_text = step.lstrip("0123456789.-) ").strip()
            agent_name = agent_sequence[i] if i < len(agent_sequence) else "ResearchAgent"
            sub = SubTask(
                id=str(uuid.uuid4())[:6],
                description=step_text,
                assigned_to=agent_name,
                depends_on=prev_id
            )
            subtasks.append(sub)
            prev_id = sub.id
            self._emit(f"Subtask {i+1}: '{step_text[:50]}' → {agent_name}")

        return subtasks

    def execute(self, goal: str, on_update=None) -> Task:
        """Full pipeline: plan → assign → run each agent → return result."""
        task = Task(id=str(uuid.uuid4())[:8], goal=goal)
        self._tasks[task.id] = task
        task.status = TaskStatus.IN_PROGRESS
        self._emit(f"🚀 Starting task [{task.id}]: {goal}")

        # Plan
        subtasks = self.plan(goal)
        task.subtasks = subtasks

        from app.agents.registry import AgentRegistry
        registry = AgentRegistry()

        previous_result = ""

        # Execute each subtask in order
        for i, subtask in enumerate(subtasks):
            subtask.status = TaskStatus.IN_PROGRESS
            subtask.started_at = datetime.now().isoformat()
            self._emit(f"▶ [{subtask.assigned_to}] Working on: {subtask.description[:60]}")

            if on_update:
                on_update(f"[{subtask.assigned_to}] {subtask.description[:60]}...")

            agent = registry.get(subtask.assigned_to)
            if not agent:
                subtask.status = TaskStatus.FAILED
                continue

            # Pass previous result as context
            task_input = subtask.description
            if previous_result:
                task_input += f"\n\nPrevious agent output:\n{previous_result}"

            # Run with retry
            result = self._run_with_retry(agent, task_input)
            subtask.result = result
            subtask.status = TaskStatus.DONE
            subtask.completed_at = datetime.now().isoformat()
            previous_result = result
            self._emit(f"✓ [{subtask.assigned_to}] Done")

        # Final result is the last agent's output
        task.final_result = previous_result
        task.status = TaskStatus.DONE
        task.completed_at = datetime.now().isoformat()
        self._emit(f"✅ Task [{task.id}] COMPLETE")
        return task

    def _run_with_retry(self, agent, task: str, max_retries: int = 3) -> str:
        """Run an agent with automatic retry."""
        for attempt in range(max_retries):
            try:
                result = agent.run(task)
                if result and not result.startswith(f"[{agent.name}] Failed"):
                    return result
            except Exception as e:
                self._emit(f"⚠ {agent.name} attempt {attempt+1} failed: {e}")
                time.sleep(1)
        # Last resort: try a different agent
        self._emit(f"🔄 Reassigning {agent.name}'s task...")
        from app.agents.registry import AgentRegistry
        backup = AgentRegistry().get("ResearchAgent")
        return backup.run(task) if backup else "Task could not be completed."

    def get_status(self, task_id: str) -> Optional[dict]:
        """Get current status of a task."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        return {
            "id": task.id,
            "goal": task.goal,
            "status": task.status,
            "subtasks": [
                {
                    "id": s.id,
                    "description": s.description,
                    "assigned_to": s.assigned_to,
                    "status": s.status,
                    "result_preview": s.result[:100] if s.result else ""
                }
                for s in task.subtasks
            ],
            "final_result": task.final_result,
            "created_at": task.created_at,
            "completed_at": task.completed_at
        }

    def get_all_tasks(self) -> List[dict]:
        return [self.get_status(tid) for tid in self._tasks]

    def get_live_updates(self) -> List[dict]:
        return self._live_updates[-50:]  # last 50 updates

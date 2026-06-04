"""
THE YC DEMO — This is what you show investors.
5 agents. 1 goal. 0 human intervention.
"""
import sys
import time
sys.path.insert(0, "/home/claude/agentos")

from app.orchestrator.orchestrator import Orchestrator, TaskStatus

def test_full_yc_demo():
    print("\n")
    print("=" * 60)
    print("  🤖 AgentOS — LIVE DEMO")
    print("  Built from a college dorm. Designed to change history.")
    print("=" * 60)

    goal = "Write a comprehensive report on Artificial Intelligence"
    print(f"\n  GOAL: {goal}")
    print("  AGENTS: PlannerAgent → ResearchAgent → WriterAgent")
    print("          → FactCheckerAgent → EditorAgent")
    print("-" * 60)

    start = time.time()
    orch = Orchestrator()
    task = orch.execute(goal)
    elapsed = round(time.time() - start, 1)

    print("\n" + "=" * 60)
    print("  📄 FINAL REPORT:")
    print("=" * 60)
    print(task.final_result)
    print("=" * 60)
    print(f"\n  ✅ STATUS:     {task.status}")
    print(f"  ⏱️  TIME:       {elapsed} seconds")
    print(f"  🤖 AGENTS:     {len(task.subtasks)}")
    print(f"  👤 HUMANS:     0")
    print("=" * 60)
    print("\n  This is AgentOS. This is your YC application.\n")

    assert task.status == TaskStatus.DONE
    assert task.final_result
    assert len(task.final_result) > 100
    assert len(task.subtasks) >= 3

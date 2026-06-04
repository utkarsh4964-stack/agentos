import sys
sys.path.insert(0, "/home/claude/agentos")

from app.orchestrator.orchestrator import Orchestrator, TaskStatus

def test_plan_creates_subtasks():
    orch = Orchestrator()
    subtasks = orch.plan("Write a report about climate change")
    assert len(subtasks) >= 2
    print(f"\n✓ Plan created {len(subtasks)} subtasks:")
    for s in subtasks:
        print(f"  - [{s.assigned_to}] {s.description[:60]}")

def test_execute_completes_goal():
    orch = Orchestrator()
    task = orch.execute("Write a short summary of solar energy")
    assert task.status == TaskStatus.DONE
    assert task.final_result
    assert len(task.final_result) > 50
    print(f"\n✓ Task executed successfully")
    print(f"  Status: {task.status}")
    print(f"  Subtasks: {len(task.subtasks)}")
    print(f"  Result preview: {task.final_result[:150]}...")

def test_get_status():
    orch = Orchestrator()
    task = orch.execute("Explain what Python is")
    status = orch.get_status(task.id)
    assert status is not None
    assert status["id"] == task.id
    assert status["status"] == "DONE"
    print(f"\n✓ get_status() works for task {task.id}")

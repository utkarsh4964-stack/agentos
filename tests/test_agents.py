import sys
sys.path.insert(0, "/home/claude/agentos")

from app.agents.base import BaseAgent
from app.agents.registry import AgentRegistry

def test_base_agent_runs_task():
    agent = BaseAgent("TestAgent", "Answer questions clearly")
    result = agent.run("What is 2 + 2?")
    assert result is not None
    assert len(result) > 0
    print(f"\n✓ Agent ran task. Output: {result[:80]}")

def test_agent_registry_registers():
    registry = AgentRegistry()
    agent = BaseAgent("MyTestAgent", "Test role")
    registry.register(agent)
    found = registry.get("MyTestAgent")
    assert found is not None
    assert found.name == "MyTestAgent"
    print("\n✓ Agent registered and retrieved")

def test_agent_registry_lists_all():
    registry = AgentRegistry()
    all_agents = registry.list_all()
    assert len(all_agents) >= 5  # 5 default agents
    print(f"\n✓ Registry has {len(all_agents)} agents: {all_agents}")

def test_find_best_agent():
    registry = AgentRegistry()
    agent = registry.find_best_agent("research and find facts about AI")
    assert agent is not None
    assert agent.name == "ResearchAgent"
    print(f"\n✓ Best agent for research task: {agent.name}")

def test_two_agents_complete_one_task():
    """THE DAY 1 CHECKPOINT — Two agents working together."""
    registry = AgentRegistry()
    researcher = registry.get("ResearchAgent")
    writer = registry.get("WriterAgent")

    # Agent 1: Research
    facts = researcher.run("Find 3 key facts about the planet Mars")
    assert facts and len(facts) > 20

    # Agent 2: Write from research
    article = writer.run(f"Write a short paragraph using these facts: {facts}")
    assert article and len(article) > 20

    print(f"\n✓ Two agents completed a task together!")
    print(f"  Researcher output: {facts[:100]}...")
    print(f"  Writer output:     {article[:100]}...")

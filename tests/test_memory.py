import sys
sys.path.insert(0, "/home/claude/agentos")

from app.memory.memory_store import MemoryStore

def test_short_term_write_read():
    memory = MemoryStore()
    memory.write("test_key", "hello world")
    result = memory.read("test_key")
    assert result == "hello world"
    print("\n✓ Short term write and read works")

def test_long_term_write_search():
    memory = MemoryStore()
    memory.write("ai_facts", "Artificial intelligence is transforming industries", long_term=True)
    results = memory.search("artificial intelligence")
    assert isinstance(results, list)
    print(f"\n✓ Long term search returned {len(results)} results")

def test_shared_memory_across_agents():
    from app.agents.base import BaseAgent
    memory = MemoryStore()

    agent_a = BaseAgent("AgentA", "Store information")
    agent_b = BaseAgent("AgentB", "Retrieve information")

    # Agent A writes
    agent_a.save_to_memory("shared_fact", "The sky is blue", long_term=True)

    # Agent B reads (same MemoryStore singleton)
    result = agent_b.memory.read("shared_fact")
    assert result == "The sky is blue"
    print("\n✓ Memory is shared across agents — same value read by different agent")

def test_get_all_memory():
    memory = MemoryStore()
    memory.write("key1", "value1")
    memory.write("key2", "value2")
    all_mem = memory.get_all()
    assert "key1" in all_mem
    assert "key2" in all_mem
    print(f"\n✓ get_all() returns {len(all_mem)} items")

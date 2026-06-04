# 🤖 AgentOS — The Operating System for AI Agents

> Built from a college dorm. Designed to change history.

AgentOS is the infrastructure layer that lets multiple AI agents share memory, communicate, delegate tasks, and work together as a team to complete any goal.

Think of it as **Windows — but for AI agents.**

---

## Architecture

```
┌─────────────────────────────────────┐
│         AgentOS KERNEL              │
│                                     │
│  Agent Registry  |  Memory Store    │
│  Task Orchestrator | Message Bus    │
│  Error Recovery  | Resource Mgr     │
└─────────────────────────────────────┘
         ↕              ↕
  🧠 Planner    🔍 Researcher    ✍️ Writer
  🔎 FactChecker    🎨 Editor
```

---

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Add your API key
echo "GEMINI_API_KEY=your_key_here" > .env

# 3. Run the server
python main.py

# 4. Open dashboard
open dashboard/index.html
```

---

## Run the YC Demo

```bash
pytest tests/test_demo.py -v -s
```

Watch 5 agents write a full research report in under 90 seconds.

---

## Run All Tests

```bash
pytest tests/ -v
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /agents | List all agents |
| POST | /agents/register | Register new agent |
| POST | /tasks/submit | Submit a goal |
| GET | /tasks/{id} | Get task status |
| GET | /tasks | List all tasks |
| GET | /memory/search?q= | Search memory |
| GET | /resources/usage | API usage + cost |
| WS | /ws/live | Live agent feed |

---

## Built for Y Combinator

AgentOS solves a real problem: every developer building multi-agent systems reinvents the same infrastructure from scratch. AgentOS is that infrastructure — built once, used everywhere.

**The 1-sentence pitch:** *AgentOS is the Windows for AI agents.*

---

*Built in 7 days. Stack: Python + FastAPI + ChromaDB + Gemini API*

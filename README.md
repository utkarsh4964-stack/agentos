# 🤖 AgentOS — The Operating System for AI Agents

> Built from a college dorm. Designed to orchestrate the next generation of AI systems.

**AgentOS is a no-code platform for building, orchestrating, and monitoring multi-agent AI workflows.**

Create specialized AI agents, connect them into pipelines, and automate complex tasks such as research, content generation, code review, analysis, and business workflows—all from a single platform.

**Think Zapier for AI agents, with built-in memory, orchestration, communication, and monitoring.**

🌐 **Live Demo:** https://agentos-production-5783.up.railway.app
📖 **API Docs:** https://agentos-production-5783.up.railway.app/docs
⭐ **Star this repository if you find it useful**

---

# 🚀 Why AgentOS?

As AI agents become more capable, developers face a new challenge:

How do multiple agents work together effectively?

Most teams eventually rebuild the same infrastructure:

* Agent orchestration
* Shared memory
* Workflow dependencies
* Inter-agent communication
* Error handling and retries
* Usage tracking
* Authentication and access control
* Monitoring and observability

Building these systems repeatedly wastes time and slows innovation.

**AgentOS provides the infrastructure layer so developers can focus on building agents instead of rebuilding the plumbing around them.**

---

# 🎯 What Can You Build?

AgentOS can power workflows such as:

* 📊 Market Research Pipelines
* ✍️ Content Generation Systems
* 💻 Automated Code Review
* 📄 Report Generation
* 📚 Knowledge Management
* 🔍 Competitive Analysis
* 🎓 Study & Research Assistants
* 🏢 Internal Business Automation

---

# ⚙️ How It Works

## 1. Create Agents

Define specialized AI agents with custom instructions.

Example:

```text
Research Agent:
"You are an expert market researcher."

Writer Agent:
"You convert research into professional reports."

Reviewer Agent:
"You validate facts and improve clarity."
```

---

## 2. Build Workflows

Connect agents into pipelines.

```text
Research
    ↓
Analysis
    ↓
Writing
    ↓
Review
```

Each agent automatically receives context from previous stages.

---

## 3. Submit a Goal

Example:

```text
Generate a competitive analysis of the AI agent market.
```

The orchestration engine coordinates the workflow automatically.

---

## 4. Monitor Execution

Track:

* Agent outputs
* Task progress
* Workflow history
* Resource usage
* Execution status

all in real time through the dashboard.

---

# ✨ Features

| Feature                   | Description                                    |
| ------------------------- | ---------------------------------------------- |
| 🤖 Custom Agents          | Create specialized AI agents with custom roles |
| 🔗 Workflow Pipelines     | Chain agents into multi-step workflows         |
| 🧠 Shared Memory          | Automatically share context between agents     |
| ⚡ Real-Time Dashboard     | Monitor workflow execution live                |
| 🔄 Automatic Retries      | Recover gracefully from failures               |
| 📡 REST API               | Full API access for integration                |
| 🔑 API Authentication     | Secure API-key based access                    |
| 📊 Usage Tracking         | Track platform usage and execution             |
| 💾 Persistent Storage     | Save workflows, tasks, and results             |
| 🚀 Cloud Deployment Ready | Designed for production deployment             |

---

# 🏗️ Architecture

```text
                    AgentOS Kernel

┌──────────────────────────────────────────────┐
│                                              │
│  Agent Registry      Shared Memory           │
│  Task Orchestrator   Message Bus             │
│  Resource Manager    Error Recovery          │
│  Authentication      Usage Tracking          │
│                                              │
└──────────────────────────────────────────────┘
                       │
                       ▼

      Planner → Researcher → Writer → Reviewer
                       │
                       ▼

          REST API + Live Dashboard
```

---

# 🔥 Example Workflow

Input:

```text
Create a report on renewable energy trends.
```

Execution:

```text
Planner Agent
      ↓
Research Agent
      ↓
Analysis Agent
      ↓
Writer Agent
      ↓
Reviewer Agent
```

Output:

```text
Professional report generated automatically.
```

---

# 📡 API Endpoints

| Method | Endpoint       | Description           |
| ------ | -------------- | --------------------- |
| POST   | /auth/signup   | Create account        |
| POST   | /auth/login    | Login                 |
| GET    | /auth/me       | Get user information  |
| GET    | /auth/usage    | Check usage           |
| POST   | /tasks/submit  | Submit workflow task  |
| GET    | /tasks         | List tasks            |
| GET    | /tasks/{id}    | Get task status       |
| GET    | /agents        | List agents           |
| GET    | /memory/search | Search shared memory  |
| WS     | /ws/live       | Live execution stream |

---

## Example API Request

```bash
curl -X POST \
https://agentos-production-5783.up.railway.app/tasks/submit \
-H "X-API-Key: YOUR_API_KEY" \
-H "Content-Type: application/json" \
-d '{
  "goal":"Generate a market analysis of AI startups"
}'
```

---

# ⚡ Quick Start

## Use the Hosted Version

1. Visit the live platform
2. Create an account
3. Generate an API key
4. Build agents
5. Launch workflows

---

## Run Locally

### Clone Repository

```bash
git clone https://github.com/utkarsh4964-stack/agentos.git
cd agentos
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

```env
GROQ_API_KEY=your_groq_api_key
APP_NAME=AgentOS
```

### Start Server

```bash
python main.py
```

Open:

```text
http://localhost:8000
```

---

# 🛠️ Tech Stack

| Layer          | Technology            |
| -------------- | --------------------- |
| Backend        | FastAPI               |
| Language       | Python 3.11           |
| AI Model       | Groq + Llama          |
| Database       | SQLite                |
| Frontend       | HTML, CSS, JavaScript |
| Deployment     | Railway               |
| Authentication | API Key System        |

---

# 📂 Project Structure

```text
agentos/

├── app/
│   ├── agents/
│   ├── orchestrator/
│   ├── memory/
│   ├── comms/
│   ├── resources/
│   ├── api/
│   ├── auth.py
│   └── database.py
│
├── dashboard/
│   ├── landing.html
│   ├── account.html
│   └── index.html
│
├── tests/
├── main.py
└── requirements.txt
```

---

# 🧪 Testing

Run all tests:

```bash
pytest tests/ -v
```

Run demo tests:

```bash
pytest tests/test_demo.py -v -s
```

---

# 🗺️ Roadmap

### Completed

* [x] Multi-agent workflows
* [x] Shared memory
* [x] API authentication
* [x] Live dashboard
* [x] Usage tracking
* [x] Persistent storage

### Upcoming

* [ ] Visual workflow builder
* [ ] Long-term memory
* [ ] Human approval steps
* [ ] Team collaboration
* [ ] Agent marketplace
* [ ] Multi-model support
* [ ] Workflow templates

---

# 🌟 Vision

The future of software is shifting from applications to autonomous agents.

Today developers build individual AI agents.

Tomorrow they will build entire ecosystems of collaborating agents.

**AgentOS aims to become the infrastructure layer that powers those ecosystems.**

---

# 👨‍💻 About the Builder

Built by **Utkarsh Sharma**

B.Tech Information Technology
JSS Academy of Technical Education, Noida

🐙 GitHub: https://github.com/utkarsh4964-stack

🌐 Live Demo: https://agentos-production-5783.up.railway.app

---

### From a college dorm to production.

Building the operating system for AI agents.

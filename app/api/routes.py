from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncio
import json
from app.auth import create_user, login_user, get_user_by_api_key
from app.agents.registry import AgentRegistry
from app.agents.base import BaseAgent
from app.orchestrator.orchestrator import Orchestrator
from app.memory.memory_store import MemoryStore
from app.resources.resource_manager import ResourceManager
from app.comms.message_bus import MessageBus

router = APIRouter()

# WebSocket connections
active_connections = []

class GoalRequest(BaseModel):
    goal: str

class AgentRequest(BaseModel):
    name: str
    role: str
    goal: Optional[str] = ""

class MessageRequest(BaseModel):
    from_agent: str
    to_agent: str
    content: str
    msg_type: Optional[str] = "TASK"

async def broadcast_update(message: str):
    """Send live update to all connected dashboards."""
    dead = []
    for ws in active_connections:
        try:
            await ws.send_text(json.dumps({"type": "update", "message": message}))
        except Exception:
            dead.append(ws)
    for ws in dead:
        active_connections.remove(ws)

# ── Agent endpoints ──────────────────────────────────────────────

@router.get("/agents")
def list_agents():
    registry = AgentRegistry()
    return {"agents": registry.get_all_status()}

@router.post("/agents/register")
def register_agent(req: AgentRequest):
    registry = AgentRegistry()
    agent = BaseAgent(req.name, req.role, req.goal)
    registry.register(agent)
    return {"status": "registered", "agent": agent.to_dict()}

# ── Task endpoints ───────────────────────────────────────────────

@router.post("/tasks/submit")
async def submit_task(req: GoalRequest):
    orchestrator = Orchestrator()

    updates = []
    def on_update(msg):
        updates.append(msg)
        asyncio.create_task(broadcast_update(msg))

    # Run in background so API returns task_id immediately
    import threading
    task_container = {}

    def run_task():
        task = orchestrator.execute(req.goal)
        task_container["task"] = task
        asyncio.run(broadcast_update(f"✅ Task complete: {req.goal[:50]}"))

    thread = threading.Thread(target=run_task)
    thread.start()
    thread.join()  # Wait for completion (sync for simplicity)

    task = task_container.get("task")
    if task:
        return {
            "task_id": task.id,
            "status": task.status,
            "goal": task.goal,
            "result_preview": task.final_result[:300] if task.final_result else "",
            "agents_used": len(task.subtasks)
        }
    return {"error": "Task failed"}

@router.get("/tasks/{task_id}")
def get_task(task_id: str):
    orchestrator = Orchestrator()
    status = orchestrator.get_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status

@router.get("/tasks")
def list_tasks():
    orchestrator = Orchestrator()
    return {"tasks": orchestrator.get_all_tasks()}

# ── Memory endpoints ─────────────────────────────────────────────

@router.get("/memory/search")
def search_memory(q: str):
    memory = MemoryStore()
    results = memory.search(q)
    return {"query": q, "results": results}

@router.get("/memory/all")
def get_all_memory():
    memory = MemoryStore()
    return {"memory": memory.get_all()}

# ── Resource endpoints ───────────────────────────────────────────

@router.get("/resources/usage")
def get_usage():
    rm = ResourceManager()
    return rm.get_total_cost()

# ── Message endpoints ────────────────────────────────────────────

@router.get("/messages")
def get_messages():
    bus = MessageBus()
    return {"messages": bus.get_all_messages()}

# ── Live updates ─────────────────────────────────────────────────

@router.get("/live/updates")
def get_live_updates():
    orchestrator = Orchestrator()
    return {"updates": orchestrator.get_live_updates()}

@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": "🤖 AgentOS Live Feed Connected"
        }))
        while True:
            # Keep alive
            await asyncio.sleep(1)
            await websocket.send_text(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
# ── Auth endpoints ───────────────────────────────────────────────

class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/auth/signup")
def signup(req: SignupRequest):
    if not req.email or not req.password:
        raise HTTPException(status_code=400, detail="Email and password required")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    result = create_user(req.email, req.password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/auth/login")
def login(req: LoginRequest):
    result = login_user(req.email, req.password)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result

@router.get("/auth/me")
def get_me(x_api_key: str = None):
    from fastapi import Header
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required. Pass X-API-Key header.")
    user = get_user_by_api_key(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {
        "email": user["email"],
        "plan": user["plan"],
        "api_key": user["api_key"],
        "created_at": user["created_at"]
    }
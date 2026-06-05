from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import asyncio
import json

from app.auth import create_user, login_user, get_user_by_api_key, check_usage_limit
from app.agents.registry import AgentRegistry
from app.agents.base import BaseAgent
from app.orchestrator.orchestrator import Orchestrator
from app.memory.memory_store import MemoryStore
from app.resources.resource_manager import ResourceManager
from app.comms.message_bus import MessageBus

router = APIRouter()
active_connections = []

class GoalRequest(BaseModel):
    goal: str

class AgentRequest(BaseModel):
    name: str
    role: str
    goal: Optional[str] = ""

class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

async def broadcast_update(message: str):
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
async def submit_task(req: GoalRequest, x_api_key: Optional[str] = Header(None)):
    # Check API key
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    user = get_user_by_api_key(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Check usage limit
    usage = check_usage_limit(x_api_key)
    if not usage["allowed"]:
        raise HTTPException(status_code=429, detail=usage["reason"])

    orchestrator = Orchestrator()
    import threading
    task_container = {}

    def run_task():
        task = orchestrator.execute(req.goal)
        task_container["task"] = task
        asyncio.run(broadcast_update(f"✅ Task complete: {req.goal[:50]}"))

    thread = threading.Thread(target=run_task)
    thread.start()
    thread.join()

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
            await asyncio.sleep(1)
            await websocket.send_text(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)

# ── Auth endpoints ───────────────────────────────────────────────

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
def get_me(x_api_key: Optional[str] = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    user = get_user_by_api_key(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {
        "email": user["email"],
        "plan": user["plan"],
        "api_key": user["api_key"],
        "created_at": user["created_at"]
    }

@router.get("/auth/usage")
def get_usage_stats(x_api_key: Optional[str] = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    usage = check_usage_limit(x_api_key)
    return usage
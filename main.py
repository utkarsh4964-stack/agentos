from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
import os

app = FastAPI(
    title="AgentOS",
    description="The Operating System for AI Agents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "name": "AgentOS",
        "version": "1.0.0",
        "status": "running",
        "message": "The Operating System for AI Agents",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    print("\n🤖 AgentOS Starting...")
    print("📡 API:       http://localhost:8000")
    print("📖 API Docs:  http://localhost:8000/docs")
    print("🎛️  Dashboard: open dashboard/index.html\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

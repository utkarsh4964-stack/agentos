from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router

DASHBOARD_DIR = Path(__file__).resolve().parent / "dashboard"

app = FastAPI(
    title="AgentOS",
    description="The Operating System for AI Agents",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", include_in_schema=False)
async def landing_page():
    """Marketing landing page."""
    return FileResponse(DASHBOARD_DIR / "landing.html")


@app.get("/dashboard", include_in_schema=False)
@app.get("/dashboard/", include_in_schema=False)
async def dashboard_page():
    """Live agent dashboard."""
    return FileResponse(DASHBOARD_DIR / "index.html")


# Other files in dashboard/ (e.g. /landing.html) — mount last so API routes win
app.mount(
    "/",
    StaticFiles(directory=str(DASHBOARD_DIR), html=False),
    name="dashboard",
)

if __name__ == "__main__":
    import uvicorn

    print("\n🤖 AgentOS Starting...")
    print("🏠 Landing:   http://localhost:8000/")
    print("🎛️  Dashboard: http://localhost:8000/dashboard")
    print("📖 API Docs:  http://localhost:8000/docs")
    print("📡 API:       http://localhost:8000\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

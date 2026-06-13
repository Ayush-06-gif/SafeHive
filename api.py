"""
FastAPI Backend — Routes requests to the SafeHive scenario engine.

Endpoints:
  POST /api/order          — Run a full food ordering scenario
  GET  /api/health         — Health check
  GET  /api/vendors        — List all vendors (honest + malicious)
  GET  /api/session/{id}   — Retrieve a saved session log
  GET  /                   — Serve the frontend UI
"""

import json
import os
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sandbox.scenarios import run_scenario
from agents.honest_vendor import get_honest_vendor_names
from agents.malicious_vendor import get_malicious_vendor_names

# ---------- app setup ----------

app = FastAPI(
    title="SafeHive",
    description="Multi-Agent AI Security Sandbox — Food Ordering Simulation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend files (CSS, JS)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Sessions directory
SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)


# ---------- request / response models ----------

class OrderRequest(BaseModel):
    user_input: str


# ---------- endpoints ----------

@app.get("/")
async def serve_frontend():
    """Serve the main frontend page."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(index_path)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "running", "message": "SafeHive active"}


@app.get("/api/vendors")
async def list_vendors():
    """List all available vendors grouped by type."""
    return {
        "honest": get_honest_vendor_names(),
        "malicious": get_malicious_vendor_names(),
    }


@app.post("/api/order")
async def place_order(request: OrderRequest):
    """
    Run a full food ordering scenario.

    Takes the user's food request, selects a vendor via the User Twin,
    runs the multi-turn conversation with guard monitoring, and returns
    the full result.
    """
    session_id = str(uuid.uuid4())[:8]

    try:
        result = await run_scenario(request.user_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario failed: {str(e)}")

    # Save session log
    session_data = {
        "session_id": session_id,
        "user_input": request.user_input,
        "result": result,
    }

    session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

    return session_data


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Retrieve a saved session log by ID."""
    session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")

    if not os.path.exists(session_file):
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    with open(session_file, "r", encoding="utf-8") as f:
        session_data = json.load(f)

    return session_data

import json
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

from .chat import router as chat_router
from .helpers import get_instance_status, load_trajectory
from .models import TRAJECTORIES_BASE_DIR, TrajectoryData, TrajectoryInfo

load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    FastAPICache.init(InMemoryBackend())
    yield


app = FastAPI(title="Agent Timeline Visualizer", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the chat router
app.include_router(chat_router)


@app.get("/")
async def root():
    return {"message": "Agent Timeline Visualizer API"}


@app.get("/api/trajectories", response_model=list[TrajectoryInfo])
@cache(expire=3600)  # Cache for 1 hour. Note: this decorator must be after the fastapi endpoint decorator
async def list_trajectories() -> list[TrajectoryInfo]:
    """List all available trajectory IDs"""
    trajectories = []
    if not TRAJECTORIES_BASE_DIR.exists() or not TRAJECTORIES_BASE_DIR.is_dir():
        # Return empty list or raise an error if the base directory doesn't exist
        return []

    # List subdirectories which represent trajectory IDs
    trajectory_dirs = [d for d in os.listdir(TRAJECTORIES_BASE_DIR) if (TRAJECTORIES_BASE_DIR / d).is_dir()]

    for traj_id in trajectory_dirs:
        # Construct the expected path for the .traj file
        traj_file_path = TRAJECTORIES_BASE_DIR / traj_id / f"{traj_id}.traj"
        if traj_file_path.exists():
            status = get_instance_status(traj_id)
            trajectories.append(TrajectoryInfo(id=traj_id, path=str(traj_file_path), status=status))

    trajectories.sort(key=lambda x: x.id)
    return trajectories


@app.get("/api/trajectories/{trajectory_id}", response_model=TrajectoryData)
@cache(expire=3600)
async def get_trajectory(trajectory_id: str) -> TrajectoryData:
    """Get detailed data for a specific trajectory"""
    traj_file_path = TRAJECTORIES_BASE_DIR / trajectory_id / f"{trajectory_id}.traj"

    if not traj_file_path.exists():
        raise HTTPException(status_code=404, detail="Trajectory file not found")

    try:
        traj_json = load_trajectory(trajectory_id)
        return TrajectoryData(**traj_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding trajectory JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing trajectory file: {str(e)}")

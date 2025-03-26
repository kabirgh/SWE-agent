import json
import os
import mmap
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from pydantic import BaseModel


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

# Path to demos directory
DEMOS_DIR = Path(__file__).parent.parent.parent / "demos"
RESULTS_PATH = Path(__file__).parent / "c37results.json"


class DemoInfo(BaseModel):
    id: str
    path: str
    status: str  # "passed" or "failed"


class ActionInfo(BaseModel):
    details: dict[str, Any] = {}
    type: str | None = None


class DemoData(BaseModel):
    id: str
    status: str  # "passed" or "failed"
    actions: list[ActionInfo]


def get_instance_status(instance_id: str) -> str:
    """Get the status of a specific instance from the results file"""
    try:
        with open(RESULTS_PATH, "r") as f:
            results = json.load(f)

        if instance_id in results.get("resolved_ids", []):
            return "passed"
        elif (
            instance_id in results.get("incomplete_ids", [])
            or instance_id in results.get("empty_patch_ids", [])
            or instance_id in results.get("unresolved_ids", [])
            or instance_id in results.get("error_ids", [])
        ):
            return "failed"
        return "unknown"
    except Exception:
        return "unknown"


def get_command_output(log_path: Path, command: str) -> str | None:
    """Extract command output from log file using memory mapping"""
    try:
        with open(log_path, "rb") as f:
            # Memory map the file
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                # Convert command to bytes for searching
                cmd_bytes = command.encode("utf-8")

                # Find the command
                pos = mm.find(cmd_bytes)
                if pos == -1:
                    return None

                # Move to after the command
                mm.seek(pos)

                # Find OBSERVATION
                while True:
                    line = mm.readline().decode("utf-8")
                    if not line:
                        break
                    if "OBSERVATION" in line:
                        # Collect output until we hit the step separator
                        output_lines = []
                        while True:
                            line = mm.readline().decode("utf-8")
                            if not line or "========================= STEP" in line:
                                break
                            output_lines.append(line.strip())
                        if output_lines:
                            return "\n".join(output_lines)
                        break

    except Exception as e:
        print(f"Error reading log file: {e}")
    return None


@app.get("/")
async def root():
    return {"message": "Agent Timeline Visualizer API"}


@app.get("/api/demos", response_model=list[DemoInfo])
@cache(expire=60)
async def get_demos():
    """List all available demos"""
    demos = []
    subdirs = [d for d in os.listdir(DEMOS_DIR) if Path(DEMOS_DIR / d).is_dir()]

    for subdir in subdirs:
        yaml_files = list(Path(DEMOS_DIR / subdir).glob("*.yaml"))
        yaml_files.extend(Path(DEMOS_DIR / subdir).glob("*.yml"))

        for yaml_file in yaml_files:
            # Remove .demo.yaml or .demo.yml suffix to get the actual demo ID
            demo_id = yaml_file.name.replace(".demo.yaml", "").replace(".demo.yml", "")
            status = get_instance_status(demo_id)
            demo_info = DemoInfo(id=demo_id, path=str(yaml_file), status=status)
            demos.append(demo_info)

    demos.sort(key=lambda x: x.id)
    return demos


@app.get("/api/demos/{demo_id}", response_model=DemoData)
async def get_demo(demo_id: str):
    """Get detailed data for a specific demo"""
    # Find the demo file
    demo_path = None
    subdirs = [d for d in os.listdir(DEMOS_DIR) if Path(DEMOS_DIR / d).is_dir()]

    for subdir in subdirs:
        yaml_files = list(Path(DEMOS_DIR / subdir).glob("*.yaml"))
        yaml_files.extend(Path(DEMOS_DIR / subdir).glob("*.yml"))

        for yaml_file in yaml_files:
            current_id = yaml_file.name.replace(".demo.yaml", "").replace(".demo.yml", "")
            if current_id == demo_id:
                demo_path = str(yaml_file)
                break
        if demo_path:
            break

    if not demo_path:
        raise HTTPException(status_code=404, detail="Demo not found")

    # Load and parse the YAML file
    try:
        with open(demo_path, "r") as file:
            yaml_data = yaml.safe_load(file)

        # Extract history items and convert them to actions
        actions = []
        for item in yaml_data.get("history", []):
            action_details = {
                "role": item.get("role"),
                "content": item.get("content"),
                "agent": item.get("agent"),
                "message_type": item.get("message_type"),
            }

            # Process each tool call as a separate action
            action_type = None
            tool_calls = item.get("tool_calls") or []
            assert len(tool_calls) <= 1, f"Expected 0 or 1 tool calls, got {len(tool_calls)}"
            for tool_call in tool_calls:
                action_type = tool_call.get("function", {}).get("name", "unknown")
                action_details["tool_call"] = tool_call

            actions.append(ActionInfo(type=action_type, details=action_details))

        status = get_instance_status(demo_id)
        return DemoData(id=demo_id, status=status, actions=actions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing demo: {str(e)}")


@app.get("/api/demos/{demo_id}/command-output")
async def get_command_output_endpoint(demo_id: str, command: str):
    """Get output for a specific command in a demo"""
    try:
        # Get log file path
        log_path = (
            Path(__file__).parent.parent.parent
            / "trajectories"
            / "root"
            / "ml_claude37__claude-3-7-sonnet-20250219__t-0.00__p-1.00__c-1.50___instances"
            / demo_id
            / f"{demo_id}.info.log"
        )

        print(demo_id)

        if not log_path.exists():
            raise HTTPException(status_code=404, detail="Log file not found")

        output = get_command_output(log_path, command)
        if output is None:
            raise HTTPException(status_code=404, detail="Command output not found")

        return {"output": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching command output: {str(e)}")


# Mount frontend static files (will be used after building the frontend)
# app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")

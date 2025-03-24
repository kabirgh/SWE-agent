from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import yaml
import glob
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Agent Timeline Visualizer")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to demos directory
DEMOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../demos"))


class DemoInfo(BaseModel):
    id: str
    name: str
    path: str


class ActionInfo(BaseModel):
    details: dict[str, Any] = {}
    type: str | None = None


class DemoData(BaseModel):
    id: str
    name: str
    actions: list[ActionInfo]


@app.get("/")
async def root():
    return {"message": "Agent Timeline Visualizer API"}


@app.get("/api/demos", response_model=list[DemoInfo])
async def get_demos():
    """List all available demos"""
    demos = []

    # Get all subdirectories in the demos dir
    subdirs = [d for d in os.listdir(DEMOS_DIR) if os.path.isdir(os.path.join(DEMOS_DIR, d))]

    for subdir in subdirs:
        # Look for YAML files in each demo directory
        yaml_files = glob.glob(os.path.join(DEMOS_DIR, subdir, "*.yaml"))
        yaml_files.extend(glob.glob(os.path.join(DEMOS_DIR, subdir, "*.yml")))

        for yaml_file in yaml_files:
            demo_id = f"{subdir}_{os.path.basename(yaml_file).replace('.yaml', '').replace('.yml', '')}"
            demos.append(DemoInfo(id=demo_id, name=f"{subdir}/{os.path.basename(yaml_file)}", path=yaml_file))

    # Sort demos alphabetically by name
    demos.sort(key=lambda x: x.name)

    return demos


@app.get("/api/demos/{demo_id}", response_model=DemoData)
async def get_demo(demo_id: str):
    """Get detailed data for a specific demo"""
    demos = await get_demos()

    # Find the demo with the matching ID
    demo = next((d for d in demos if d.id == demo_id), None)
    if not demo:
        raise HTTPException(status_code=404, detail="Demo not found")

    # Load and parse the YAML file
    try:
        with open(demo.path, "r") as file:
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

        return DemoData(id=demo_id, name=demo.name, actions=actions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing demo: {str(e)}")


# Mount frontend static files (will be used after building the frontend)
# app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")

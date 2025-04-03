from pathlib import Path
from typing import Any

from pydantic import BaseModel

RESULTS_PATH = Path(__file__).parent / "c37results.json"
# Path to trajectories directory (assuming the structure observed)
TRAJECTORIES_BASE_DIR = (
    Path(__file__).parent.parent.parent
    / "trajectories"
    / "root"
    / "ml_claude37__claude-3-7-sonnet-20250219__t-0.00__p-1.00__c-1.50___instances"
)


class TrajectoryStep(BaseModel):
    action: str | None = None
    observation: str | None = None
    response: str | None = None
    thought: str | None = None
    execution_time: float | None = None
    state: dict[str, Any] | None = None
    messages: list[dict[str, Any]] | None = None
    extra_info: dict[str, Any] | None = None


class TrajectoryData(BaseModel):
    trajectory: list[TrajectoryStep]


class TrajectoryInfo(BaseModel):
    id: str
    path: str
    status: str


class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    contextId: str


class ChatResponse(BaseModel):
    role: str
    content: str

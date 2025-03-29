import json
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY", "api-key-not-found"),
)


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


# Models for Chat API
class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    contextData: TrajectoryData | None = None
    contextId: str | None = None


class ChatResponse(BaseModel):
    role: str
    content: str


# Models for listing trajectories
class TrajectoryInfo(BaseModel):
    id: str
    path: str
    status: str


def get_instance_status(instance_id: str) -> str:
    """Get the status of a specific instance from the results file"""
    try:
        with open(RESULTS_PATH) as f:
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


@app.get("/")
async def root():
    return {"message": "Agent Timeline Visualizer API"}


def stream_text(messages: list[ChatCompletionMessageParam]):
    """Stream chat completion responses"""
    try:
        # Call OpenAI API via OpenRouter
        stream = client.chat.completions.create(
            model="google/gemini-2.0-flash-thinking-exp:free",
            messages=messages,
            stream=True,
        )

        # Process the streaming response
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                # Stream the response as JSON chunks - the key difference is we don't increment the index
                # This allows the AI SDK to properly concatenate the chunks as one continuous message
                content = chunk.choices[0].delta.content
                yield f"0:{json.dumps(content)}\n"

        # Send end of stream marker with token usage if available
        usage = {}
        if hasattr(chunk, "usage") and chunk.usage:
            usage = {
                "promptTokens": chunk.usage.prompt_tokens,
                "completionTokens": chunk.usage.completion_tokens,
            }
        else:
            usage = {"promptTokens": 0, "completionTokens": 0}

        yield f'e:{{"finishReason":"stop","usage":{json.dumps(usage)},"isContinued":false}}\n'

    except Exception as e:
        # Handle errors in the streaming response
        error_message = f"Error generating response: {str(e)}"
        yield f"0:{json.dumps(error_message)}\n"
        yield 'e:{"finishReason":"error","usage":{"promptTokens":0,"completionTokens":0},"isContinued":false}\n'


@app.post("/api/chat")
async def handle_chat(request: ChatRequest, protocol: str = Query("data")):
    """Process a chat request and return a streaming response"""
    try:
        # Prepare messages for the API call
        messages = []

        # Add system message with context if available
        context = ""
        if request.contextId and request.contextData and request.contextData.trajectory:
            context = f"Analyzing trajectory {request.contextId}. "

            # Extract relevant step information from TrajectoryData
            step_summaries = []
            for i, step in enumerate(request.contextData.trajectory):
                summary_parts = []
                # Add action if present
                if step.action:
                    action_preview = step.action.strip().split("\n")[0]
                    summary_parts.append(f"Action: {action_preview[:70]}{'...' if len(action_preview) > 70 else ''}")
                # Add observation if present (often command output)
                if step.observation:
                    obs_preview = step.observation.strip().split("\n")[0]
                    summary_parts.append(f"Observation: {obs_preview[:70]}{'...' if len(obs_preview) > 70 else ''}")
                # Add response if present
                elif step.response:
                    resp_preview = step.response.strip().split("\n")[0]
                    summary_parts.append(f"Response: {resp_preview[:70]}{'...' if len(resp_preview) > 70 else ''}")
                # Add thought if present
                elif step.thought:
                    thought_preview = step.thought.strip().split("\n")[0]
                    summary_parts.append(f"Thought: {thought_preview[:70]}{'...' if len(thought_preview) > 70 else ''}")

                if summary_parts:
                    step_summaries.append(f"Step {i + 1}: {'; '.join(summary_parts)}")

            if step_summaries:
                if len(step_summaries) > 10:
                    context += "Key steps include: " + "; ".join(step_summaries[:5] + ["..."] + step_summaries[-5:])
                else:
                    context += "Steps include: " + "; ".join(step_summaries)

        if context:
            messages.append(
                {
                    "role": "system",
                    "content": f"You are an assistant helping analyze software engineering agent execution trajectories. {context}",
                }
            )
        else:
            messages.append(
                {"role": "system", "content": "You are an assistant helping analyze agent execution trajectories."}
            )

        # Add conversation history
        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})

        # Return a streaming response
        response = StreamingResponse(stream_text(messages))
        response.headers["x-vercel-ai-data-stream"] = "v1"
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.get("/api/trajectories", response_model=list[TrajectoryInfo])
@cache(expire=3600)  # Cache for 1 hour. Note: this decorator must be after the fastapi endpoint decorator
async def list_trajectories():
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
async def get_trajectory(trajectory_id: str):
    """Get detailed data for a specific trajectory"""
    traj_file_path = TRAJECTORIES_BASE_DIR / trajectory_id / f"{trajectory_id}.traj"

    if not traj_file_path.exists():
        raise HTTPException(status_code=404, detail="Trajectory file not found")

    try:
        with open(traj_file_path) as f:
            # Load the JSON data directly
            data = json.load(f)

            # Remove 'messages' field from each step in the trajectory
            if "trajectory" in data and isinstance(data["trajectory"], list):
                for step in data["trajectory"]:
                    if isinstance(step, dict):
                        step.pop("messages", None)

            # Validate the data against the Pydantic model
            return TrajectoryData(**data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding trajectory JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing trajectory file: {str(e)}")

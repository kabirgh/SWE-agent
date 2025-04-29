import json
import os

from dotenv import load_dotenv
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from .helpers import load_pr_description, load_trajectory
from .models import ChatRequest

router = APIRouter()

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.getenv("OPENROUTER_API_KEY", "api-key-not-found"),
)


SYSTEM_PROMPT = """
You are an assistant helping analyze trajectories for SWE-Agent, a software engineering agent that solves real world tasks taken from GitHub. You don't know whether the agent has correctly solved the trajactory provided.

The agent is given these instructions:
<instructions>
Follow these steps to resolve the issue:
1. As a first step, it might be a good idea to find and read code relevant to the <pr_description>
2. Create a script to reproduce the error and execute it using the bash tool, to confirm the error
3. Edit the sourcecode of the repo to resolve the issue
4. Rerun your reproduce script and confirm that the error is fixed!
5. Think about edgecases and make sure your fix handles them as well
</instructions>

These are the main tools available to the agent:
<tools>
str_replace_editor: Custom editing tool for viewing, creating and editing files
bash: execute bash commands
submit: submit the agent's changes
</tools>

This is the description of the task the agent is trying to solve:
<pr_description>
{pr_description}
</pr_description>

Here is the trajectory:
<trajectory>
{trajectory_json}
</trajectory>
"""


def stream_text(messages: list[ChatCompletionMessageParam]):
    """Stream chat completion responses"""
    try:
        stream = client.chat.completions.create(
            model="google/gemini-2.0-flash-thinking-exp:free",
            messages=messages,
            stream=True,
        )

        # Process the streaming response
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield f"0:{json.dumps(content)}\n"

        # Send end of stream marker with token usage if available
        usage = {}
        if "chunk" in locals() and hasattr(chunk, "usage") and chunk.usage:
            usage = {
                "promptTokens": chunk.usage.prompt_tokens,
                "completionTokens": chunk.usage.completion_tokens,
            }
        else:
            usage = {"promptTokens": 0, "completionTokens": 0}

        # Specific format required by ai sdk in the frontend
        yield f'e:{{"finishReason":"stop","usage":{json.dumps(usage)},"isContinued":false}}\n'

    except Exception as e:
        error_message = f"Error generating response: {str(e)}"
        yield f"0:{json.dumps(error_message)}\n"
        # Specific format required by ai sdk in the frontend
        yield 'e:{"finishReason":"error","usage":{"promptTokens":0,"completionTokens":0},"isContinued":false}\n'


@router.post("/api/chat")
async def handle_chat(request: ChatRequest, protocol: str = Query("data")):
    """Process a chat request and return a streaming response"""
    traj_json = load_trajectory(request.contextId)
    pr_description = load_pr_description(request.contextId)

    system_prompt = SYSTEM_PROMPT.format(pr_description=pr_description, trajectory_json=traj_json)

    messages = []
    messages.append(
        {
            "role": "system",
            "content": f"{system_prompt}",
        }
    )

    # Add conversation history
    for msg in request.messages:
        messages.append({"role": msg.role, "content": msg.content})

    # Return a streaming response
    response = StreamingResponse(stream_text(messages))
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response


@router.post("/api/analyze")
async def handle_analyze(request: ChatRequest):
    traj_json = load_trajectory(request.contextId)
    pr_description = load_pr_description(request.contextId)

    system_prompt = SYSTEM_PROMPT.format(pr_description=pr_description, trajectory_json=traj_json)

    messages = []
    messages.append(
        {
            "role": "system",
            "content": f"{system_prompt}",
        }
    )
    messages.append(
        {
            "role": "user",
            "content": """
Analyze the trajectory and provide the following information:
1. A summary of the key steps and outcomes
2. Places where the agent made mistakes, had an important insight, did something unexpected, or attempted to cheat
""",
        }
    )

    # Add conversation history
    for msg in request.messages:
        messages.append({"role": msg.role, "content": msg.content})

    # Return a streaming response
    response = StreamingResponse(stream_text(messages))
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response

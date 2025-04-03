import json
import mmap
from functools import lru_cache

from .models import RESULTS_PATH, TRAJECTORIES_BASE_DIR


@lru_cache(maxsize=128)
def load_trajectory(trajectory_id: str) -> dict:
    traj_file_path = TRAJECTORIES_BASE_DIR / trajectory_id / f"{trajectory_id}.traj"
    with open(traj_file_path) as f:
        data = json.load(f)

    # Remove 'messages' field from each step in the trajectory
    if "trajectory" in data and isinstance(data["trajectory"], list):
        for step in data["trajectory"]:
            if isinstance(step, dict):
                step.pop("messages", None)

    return data


@lru_cache(maxsize=128)
def load_pr_description(trajectory_id: str) -> str:
    log_file_path = TRAJECTORIES_BASE_DIR / trajectory_id / f"{trajectory_id}.info.log"

    with open(log_file_path, "r+b") as f:
        # Memory-map the file
        mm = mmap.mmap(f.fileno(), 0)

        # Find start and end positions
        start_pattern = b"<pr_description>"
        end_pattern = b"</pr_description>"

        start_pos = mm.find(start_pattern)
        if start_pos == -1:
            mm.close()
            return ""

        start_pos += len(start_pattern)
        mm.seek(start_pos)

        end_pos = mm.find(end_pattern, start_pos)
        if end_pos == -1:
            mm.close()
            return ""

        # Extract the description
        description = mm.read(end_pos - start_pos).decode("utf-8")
        mm.close()

        return description


@lru_cache(maxsize=128)
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

from collections import Counter
from pathlib import Path
import numpy as np
from tabulate import tabulate

from .helpers import load_trajectory
from .main import get_instance_status
from .models import TRAJECTORIES_BASE_DIR, TrajectoryData
from .actions import get_action_type, REPO_TO_LANGUAGE


def calculate_percentiles(data, percentiles=[50, 90]):
    """Calculate specified percentiles for a list of numbers."""
    if not data:
        return {p: 0 for p in percentiles}
    return {p: np.percentile(data, p) for p in percentiles}


def analyze_trajectory_stats():
    """Analyze and print statistics about all trajectories."""
    # Initialize data structures
    trajectory_lengths = []
    action_counts = Counter()
    status_counts = Counter()
    language_stats = {}  # language -> {lengths: [], actions: Counter(), status: Counter()}
    processed_count = 0
    load_failed_count = 0

    print(f"\nProcessing trajectories in {TRAJECTORIES_BASE_DIR}...")

    # Iterate through trajectory directories
    for item in TRAJECTORIES_BASE_DIR.iterdir():
        if not item.is_dir():
            continue

        traj_id = item.name

        if traj_id == "tokio-rs__tokio-3852":
            print(f"Skipping {traj_id} because it doesn't have a trajectory")
            continue

        try:
            trajectory_data = TrajectoryData(**load_trajectory(traj_id))
            status = get_instance_status(traj_id)
        except Exception as e:
            print(f"Failed to load trajectory {traj_id}: {e}")
            load_failed_count += 1
            continue

        processed_count += 1
        status_counts[status] += 1

        # Get trajectory length and actions
        trajectory_length = len(trajectory_data.trajectory)
        trajectory_lengths.append(trajectory_length)

        # Count actions
        for step in trajectory_data.trajectory:
            if step.action:
                action_type = get_action_type(step.action)
                action_counts[action_type] += 1

        # Get language and update language stats
        repo_name = traj_id.rsplit("-", 1)[0].replace("__", "/")
        language = REPO_TO_LANGUAGE.get(repo_name, "unknown")

        if language not in language_stats:
            language_stats[language] = {"lengths": [], "actions": Counter(), "status": Counter()}

        language_stats[language]["lengths"].append(trajectory_length)
        language_stats[language]["status"][status] += 1

        for step in trajectory_data.trajectory:
            if step.action:
                action_type = get_action_type(step.action)
                language_stats[language]["actions"][action_type] += 1

    # Print overall statistics
    print("\n=== Overall Statistics ===")
    print(f"Total trajectories processed: {processed_count}")
    if load_failed_count > 0:
        print(f"Failed to load {load_failed_count} trajectories")

    print("\nTrajectory Length Statistics:")
    print(f"Average length: {np.mean(trajectory_lengths):.1f} steps")
    percentiles = calculate_percentiles(trajectory_lengths)
    print(f"Median (p50) length: {percentiles[50]:.1f} steps")
    print(f"p90 length: {percentiles[90]:.1f} steps")

    print("\nStatus Distribution:")
    for status, count in status_counts.most_common():
        percentage = (count / processed_count) * 100
        print(f"{status}: {count} ({percentage:.1f}%)")

    print("\nAction Type Distribution:")
    total_actions = sum(action_counts.values())
    action_table = []
    for action, count in action_counts.most_common():
        percentage = (count / total_actions) * 100
        action_table.append([action, count, f"{percentage:.1f}%"])
    print(tabulate(action_table, headers=["Action Type", "Count", "Percentage"]))

    # Print language-specific statistics
    print("\n=== Language-Specific Statistics ===")
    language_table = []
    for language, stats in language_stats.items():
        if not stats["lengths"]:
            continue

        avg_length = np.mean(stats["lengths"])
        p50_length = np.percentile(stats["lengths"], 50)
        p90_length = np.percentile(stats["lengths"], 90)

        total_trajs = sum(stats["status"].values())
        passed = stats["status"].get("passed", 0)
        success_rate = (passed / total_trajs * 100) if total_trajs > 0 else 0

        language_table.append(
            [
                language,
                total_trajs,
                f"{avg_length:.1f}",
                f"{p50_length:.1f}",
                f"{p90_length:.1f}",
                f"{success_rate:.1f}%",
            ]
        )

    print(
        tabulate(
            language_table,
            headers=["Language", "Trajectories", "Avg Length", "P50 Length", "P90 Length", "Success Rate"],
            tablefmt="grid",
        )
    )


if __name__ == "__main__":
    analyze_trajectory_stats()

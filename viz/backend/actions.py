from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate

from .helpers import load_trajectory
from .main import get_instance_status
from .models import TRAJECTORIES_BASE_DIR, TrajectoryData

# Determine the script's directory and project root directory
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.resolve()
# Create output directory for graphs
GRAPH_OUTPUT_DIR = SCRIPT_DIR / "graphs"
GRAPH_OUTPUT_DIR.mkdir(exist_ok=True)

REPO_TO_LANGUAGE = {
    "apache/druid": "java",
    "apache/lucene": "java",
    "astral-sh/ruff": "rust",
    "axios/axios": "javascript",
    "babel/babel": "javascript",
    "briannesbitt/carbon": "php",
    "burntsushi/ripgrep": "rust",
    "caddyserver/caddy": "go",
    "facebook/docusaurus": "javascript",
    "faker-ruby/faker": "ruby",
    "fastlane/fastlane": "ruby",
    "fluent/fluentd": "ruby",
    "fmtlib/fmt": "c",
    "gin-gonic/gin": "go",
    "gohugoio/hugo": "go",
    "google/gson": "java",
    "hashicorp/terraform": "go",
    "immutable-js/immutable-js": "javascript",
    "javaparser/javaparser": "java",
    "jekyll/jekyll": "ruby",
    "jordansissel/fpm": "ruby",
    "jqlang/jq": "c",
    "laravel/framework": "php",
    "micropython/micropython": "c",
    "mrdoob/three.js": "javascript",
    "nlohmann/json": "c",
    "nushell/nushell": "rust",
    "php-cs-fixer/php-cs-fixer": "php",
    "phpoffice/phpspreadsheet": "php",
    "preactjs/preact": "javascript",
    "projectlombok/lombok": "java",
    "prometheus/prometheus": "go",
    "reactivex/rxjava": "java",
    "redis/redis": "c",
    "rubocop/rubocop": "ruby",
    "sharkdp/bat": "rust",
    "tokio-rs/axum": "rust",
    "tokio-rs/tokio": "rust",
    "uutils/coreutils": "rust",
    "valkey-io/valkey": "c",
    "vuejs/core": "javascript",
}


def analyze_trajectories():
    """Loads data, analyzes trajectories, and creates graphs."""
    # Initialize data structures
    passed_action_counts = Counter()
    failed_action_counts = Counter()
    passed_trajectory_lengths = []
    failed_trajectory_lengths = []
    processed_trajectory_count = 0
    unknown_status_count = 0
    load_failed_count = 0

    # For per-trajectory action type percentages
    passed_trajectory_action_percentages = {}
    failed_trajectory_action_percentages = {}

    # For language-specific analysis
    language_action_counts = {}  # Key: language, Value: {passed: Counter(), failed: Counter()}
    # NEW: For per-language, per-trajectory action percentages
    language_trajectory_percentages = {}  # Key: language, Value: {passed: {action: [%]}, failed: {action: [%]}}

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

        if status not in ["passed", "failed"]:
            unknown_status_count += 1
            continue

        processed_trajectory_count += 1

        trajectory_length = len(trajectory_data.trajectory)
        # Count actions by type for this trajectory
        traj_action_counts = Counter()
        total_traj_actions = 0

        for step in trajectory_data.trajectory:
            if step.action:
                action_type = get_action_type(step.action)
                traj_action_counts[action_type] += 1
                total_traj_actions += 1

        # Extract repository name from traj_id
        repo_name = traj_id.rsplit("-", 1)[0].replace("__", "/")

        # Get language for this repository
        language = REPO_TO_LANGUAGE.get(repo_name, "unknown")

        # Initialize language data if not exists
        if language not in language_action_counts:
            language_action_counts[language] = {"passed": Counter(), "failed": Counter()}
            language_trajectory_percentages[language] = {"passed": {}, "failed": {}}

        # Calculate percentages for this trajectory
        if total_traj_actions > 0:
            traj_action_percentages = {
                action: (count / total_traj_actions) * 100 for action, count in traj_action_counts.items()
            }

            # Store percentages by action type
            if status == "passed":
                passed_trajectory_lengths.append(trajectory_length)
                # Add to overall counts
                passed_action_counts.update(traj_action_counts)
                # Store percentages for this trajectory
                for action_type, percentage in traj_action_percentages.items():
                    if action_type not in passed_trajectory_action_percentages:
                        passed_trajectory_action_percentages[action_type] = []
                    passed_trajectory_action_percentages[action_type].append(percentage)

                    # Store percentages by language
                    if action_type not in language_trajectory_percentages[language]["passed"]:
                        language_trajectory_percentages[language]["passed"][action_type] = []
                    language_trajectory_percentages[language]["passed"][action_type].append(percentage)

                # Add to language-specific counts
                language_action_counts[language]["passed"].update(traj_action_counts)
            else:  # status == 'failed'
                failed_trajectory_lengths.append(trajectory_length)
                # Add to overall counts
                failed_action_counts.update(traj_action_counts)
                # Store percentages for this trajectory
                for action_type, percentage in traj_action_percentages.items():
                    if action_type not in failed_trajectory_action_percentages:
                        failed_trajectory_action_percentages[action_type] = []
                    failed_trajectory_action_percentages[action_type].append(percentage)

                    # Store percentages by language
                    if action_type not in language_trajectory_percentages[language]["failed"]:
                        language_trajectory_percentages[language]["failed"][action_type] = []
                    language_trajectory_percentages[language]["failed"][action_type].append(percentage)

                # Add to language-specific counts
                language_action_counts[language]["failed"].update(traj_action_counts)

    print(f"Processed {processed_trajectory_count} trajectories.")
    if unknown_status_count > 0:
        print(f"Skipped {unknown_status_count} trajectories with unknown status.")
    if load_failed_count > 0:
        print(f"Failed to load {load_failed_count} trajectory files.")

    # --- Calculate Statistics ---
    print("\nCalculating statistics and generating graphs...")

    # Total Action Counts
    total_passed_actions = sum(passed_action_counts.values())
    total_failed_actions = sum(failed_action_counts.values())

    # Calculate action frequencies based on the previously classified actions
    passed_action_freq = (
        {action: (count / total_passed_actions) * 100 for action, count in passed_action_counts.items()}
        if total_passed_actions > 0
        else {}
    )

    failed_action_freq = (
        {action: (count / total_failed_actions) * 100 for action, count in failed_action_counts.items()}
        if total_failed_actions > 0
        else {}
    )

    # Create graphs
    # 1. Action frequency distribution overlaying passed and failed trajectories
    create_combined_action_frequency_graph(
        passed_action_freq,
        failed_action_freq,
        passed_trajectory_action_percentages,
        failed_trajectory_action_percentages,
    )

    # 2. Language-specific action frequency graphs
    create_language_graphs(language_action_counts, language_trajectory_percentages)

    print(f"\nGraphs have been saved to {GRAPH_OUTPUT_DIR}")


def create_combined_action_frequency_graph(passed_freq, failed_freq, passed_percentages, failed_percentages):
    """Create line graphs showing action frequency distribution across percentiles for both passed and failed trajectories."""
    if not passed_freq and not failed_freq:
        print("No actions found for both passed and failed trajectories.")
        return

    # Create two separate plots for passed and failed trajectories
    for status, percentages, action_freq in [
        ("passed", passed_percentages, passed_freq),
        ("failed", failed_percentages, failed_freq),
    ]:
        plt.figure(figsize=(14, 8))

        # Define percentile range for x-axis
        percentiles = np.linspace(0, 100, 101)  # 0 to 100 percentiles

        # Plot a line for each action type
        for i, (action, values) in enumerate(percentages.items()):
            if len(values) < 5:  # Skip if not enough data points
                continue

            # Calculate percentile values
            percentile_values = [np.percentile(values, p) for p in percentiles]

            # Plot the line
            plt.plot(percentiles, percentile_values, label=action, linewidth=2)

            # Add a marker at the median value
            median_value = np.median(values)
            plt.scatter(50, median_value, s=80, zorder=5)

            # Add a text label for the action at the end of the line
            plt.text(101, percentile_values[-1], action, fontsize=9, verticalalignment="center")

        # Add average frequency as dotted horizontal lines
        for action, freq in action_freq.items():
            if action in percentages and len(percentages[action]) >= 5:
                plt.axhline(y=freq, color="gray", linestyle="--", alpha=0.5)
                plt.text(0, freq, f"{freq:.1f}%", fontsize=8, verticalalignment="bottom")

        # Add graph styling
        plt.xlabel("Percentile")
        plt.ylabel("Frequency (%)")
        plt.title(f"Action Frequency Distribution for {status.capitalize()} Trajectories")
        plt.grid(True, alpha=0.3)

        # Add legend if not too cluttered (can be commented out if too many action types)
        if len(percentages) <= 10:
            plt.legend(loc="upper left")

        plt.tight_layout()
        plt.savefig(GRAPH_OUTPUT_DIR / f"action_frequency_{status}_line.png", dpi=300)
        plt.close()

    # Create a combined plot comparing passed vs failed for the most common actions
    create_comparative_line_graph(passed_percentages, failed_percentages, passed_freq, failed_freq)


def create_comparative_line_graph(passed_percentages, failed_percentages, passed_freq, failed_freq):
    """Create a line graph comparing the top action types between passed and failed trajectories."""
    # Find common actions with enough data points
    common_actions = set()
    for action in passed_percentages:
        if (
            action in failed_percentages
            and len(passed_percentages[action]) >= 5
            and len(failed_percentages[action]) >= 5
        ):
            common_actions.add(action)

    # Get the top 5 most common actions
    all_actions = list(common_actions)
    if not all_actions:
        print("Not enough common actions with sufficient data points for comparison.")
        return

    # Sort by average frequency
    all_actions.sort(key=lambda x: (passed_freq.get(x, 0) + failed_freq.get(x, 0)), reverse=True)
    top_actions = all_actions[:5]  # Use top 5 actions

    plt.figure(figsize=(14, 8))
    percentiles = np.linspace(0, 100, 101)

    # Get default color cycle from matplotlib
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    # Plot both passed and failed for each action with same color
    for i, action in enumerate(top_actions):
        color = colors[i % len(colors)]  # Use same color for both passed and failed

        # Passed trajectories - solid line
        passed_values = [np.percentile(passed_percentages[action], p) for p in percentiles]
        plt.plot(percentiles, passed_values, label=f"{action} (Passed)", linestyle="-", color=color)

        # Failed trajectories - dashed line with same color
        failed_values = [np.percentile(failed_percentages[action], p) for p in percentiles]
        plt.plot(percentiles, failed_values, label=f"{action} (Failed)", linestyle="--", color=color)

    plt.xlabel("Percentile")
    plt.ylabel("Frequency (%)")
    plt.title("Comparison of Action Frequency Distributions: Passed vs Failed")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(GRAPH_OUTPUT_DIR / "action_frequency_comparison_line.png", dpi=300)
    plt.close()


def create_action_frequency_graph(action_freq, status, trajectory_percentages):
    """Create a line graph showing action frequency distribution across percentiles."""
    if not action_freq:
        print(f"No actions found for {status} trajectories.")
        return

    plt.figure(figsize=(12, 8))
    percentiles = np.linspace(0, 100, 101)

    # Plot a line for each action type
    for action, values in trajectory_percentages.items():
        if len(values) < 5:  # Skip if not enough data points
            continue

        percentile_values = [np.percentile(values, p) for p in percentiles]
        plt.plot(percentiles, percentile_values, label=action, linewidth=2)

        # Add average frequency as dotted horizontal line
        avg_freq = action_freq.get(action, 0)
        plt.axhline(y=avg_freq, color="gray", linestyle="--", alpha=0.5)
        plt.text(0, avg_freq, f"{avg_freq:.1f}%", fontsize=8, verticalalignment="bottom")

    plt.xlabel("Percentile")
    plt.ylabel("Frequency (%)")
    plt.title(f"Action Frequency Distribution for {status.capitalize()} Trajectories")
    plt.grid(True, alpha=0.3)

    if len(trajectory_percentages) <= 10:
        plt.legend()

    plt.tight_layout()
    plt.savefig(GRAPH_OUTPUT_DIR / f"action_frequency_{status}.png", dpi=300)
    plt.close()


def create_language_graphs(language_action_counts, language_trajectory_percentages):
    """Create graphs comparing action frequencies across different programming languages."""
    # Filter to include only languages with sufficient data
    min_actions = 10  # Minimum number of actions to include a language
    valid_languages = {}

    for language, status_counts in language_action_counts.items():
        total_passed = sum(status_counts["passed"].values())
        total_failed = sum(status_counts["failed"].values())

        if total_passed + total_failed >= min_actions:
            valid_languages[language] = {
                "passed": {
                    action: (count / total_passed * 100)
                    for action, count in status_counts["passed"].items()
                    if total_passed > 0
                },
                "failed": {
                    action: (count / total_failed * 100)
                    for action, count in status_counts["failed"].items()
                    if total_failed > 0
                },
                "total_passed": total_passed,
                "total_failed": total_failed,
                "trajectory_percentages": language_trajectory_percentages[language],
            }

            # If there are no passed or failed trajectories, initialize empty dicts
            if total_passed == 0:
                valid_languages[language]["passed"] = {}
            if total_failed == 0:
                valid_languages[language]["failed"] = {}

    # Get unique action types across all languages
    all_actions = set()
    for lang_data in valid_languages.values():
        all_actions.update(lang_data["passed"].keys())
        all_actions.update(lang_data["failed"].keys())

    all_actions = sorted(list(all_actions))

    # Create a summary table of language data
    language_summary = []
    for language, data in valid_languages.items():
        language_summary.append(
            [language, data["total_passed"], data["total_failed"], data["total_passed"] + data["total_failed"]]
        )

    # Sort the language summary by total actions (index 3)
    sorted_summary = sorted(language_summary, key=lambda x: x[3], reverse=True)

    # Print summary table
    print("\nLanguage Action Summary:")
    print(
        tabulate(
            sorted_summary,
            headers=["Language", "Passed Actions", "Failed Actions", "Total Actions"],
        )
    )

    # Create graphs for each language using line graphs
    for language, data in valid_languages.items():
        create_language_line_graph(language, data)

    # Create a combined comparison graph for all languages
    create_language_comparison_graph(valid_languages, all_actions)


def create_language_line_graph(language, data):
    """Create a percentile distribution line graph for a specific language comparing action frequencies."""
    # Get the trajectory percentages
    trajectory_percentages = data["trajectory_percentages"]

    # Check if we have enough data for both passed and failed
    passed_percentages = trajectory_percentages["passed"]
    failed_percentages = trajectory_percentages["failed"]

    # Combine actions from both passed and failed
    all_actions = set()
    for status in ["passed", "failed"]:
        for action, values in trajectory_percentages[status].items():
            if len(values) >= 5:  # At least 5 trajectories for meaningful percentiles
                all_actions.add(action)

    # Skip if no actions with enough data
    if not all_actions:
        # Fall back to bar chart if not enough trajectory data
        create_language_bar_graph(language, data, "combined")
        return

    plt.figure(figsize=(14, 8))
    percentiles = np.linspace(0, 100, 101)  # 0 to 100 percentiles

    # Get default color cycle from matplotlib
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    action_colors = {action: colors[i % len(colors)] for i, action in enumerate(sorted(all_actions))}

    # Plot both passed and failed for each action
    for action in sorted(all_actions):
        color = action_colors[action]  # Same color for both passed and failed

        # Plot passed trajectories with solid line
        if action in passed_percentages and len(passed_percentages[action]) >= 5:
            values = passed_percentages[action]
            percentile_values = [np.percentile(values, p) for p in percentiles]
            plt.plot(percentiles, percentile_values, label=f"{action} (Passed)", linewidth=2, color=color)

            # Add average frequency as dotted horizontal line if available
            if action in data["passed"]:
                avg_freq = data["passed"][action]
                plt.axhline(y=avg_freq, color="gray", linestyle=":", alpha=0.3)
                plt.text(0, avg_freq, f"{avg_freq:.1f}% (P)", fontsize=7, verticalalignment="bottom")

        # Plot failed trajectories with dashed line
        if action in failed_percentages and len(failed_percentages[action]) >= 5:
            values = failed_percentages[action]
            percentile_values = [np.percentile(values, p) for p in percentiles]
            plt.plot(
                percentiles, percentile_values, label=f"{action} (Failed)", linestyle="--", linewidth=2, color=color
            )

            # Add average frequency as dotted horizontal line if available
            if action in data["failed"]:
                avg_freq = data["failed"][action]
                plt.axhline(y=avg_freq, color="gray", linestyle=":", alpha=0.3)
                plt.text(0, avg_freq, f"{avg_freq:.1f}% (F)", fontsize=7, verticalalignment="bottom")

    # Add graph styling
    plt.xlabel("Percentile")
    plt.ylabel("Frequency (%)")
    plt.title(f"Action Frequency Distribution for {language.capitalize()} - Passed vs Failed")
    plt.grid(True, alpha=0.3)

    # Add legend with reasonable size
    if len(all_actions) <= 8:
        plt.legend(loc="upper left")

    plt.tight_layout()
    plt.savefig(GRAPH_OUTPUT_DIR / f"language_{language}_combined_line.png", dpi=300)
    plt.close()

    # Create the separate graphs as well for backward compatibility
    for status in ["passed", "failed"]:
        action_percentages = trajectory_percentages[status]
        # Skip if no data for this status
        if not action_percentages:
            continue

        # Check if we have enough data points for percentiles
        has_enough_data = False
        for values in action_percentages.values():
            if len(values) >= 5:  # At least 5 trajectories for meaningful percentiles
                has_enough_data = True
                break

        if not has_enough_data:
            # Fall back to bar chart if not enough trajectory data
            create_language_bar_graph(language, data, status)
            continue

        # Create separate charts (original functionality) - code here is kept for backward compatibility
        plt.figure(figsize=(14, 8))

        # Plot a line for each action type that has sufficient data
        for action, values in action_percentages.items():
            if len(values) < 5:  # Skip if not enough data points
                continue

            percentile_values = [np.percentile(values, p) for p in percentiles]
            plt.plot(percentiles, percentile_values, label=action, linewidth=2)

            # Add a marker at the median value
            median_value = np.median(values)
            plt.scatter(50, median_value, s=80, zorder=5)

            # Add a text label for the action at the end of the line
            plt.text(101, percentile_values[-1], action, fontsize=9, verticalalignment="center")

            # Add average frequency as dotted horizontal line if available
            if action in data[status]:
                avg_freq = data[status][action]
                plt.axhline(y=avg_freq, color="gray", linestyle="--", alpha=0.5)
                plt.text(0, avg_freq, f"{avg_freq:.1f}%", fontsize=8, verticalalignment="bottom")

        # Add graph styling
        plt.xlabel("Percentile")
        plt.ylabel("Frequency (%)")
        plt.title(f"Action Frequency Distribution for {language.capitalize()} - {status.capitalize()}")
        plt.grid(True, alpha=0.3)

        # Add legend if not too cluttered
        if len([a for a, v in action_percentages.items() if len(v) >= 5]) <= 10:
            plt.legend(loc="upper left")

        plt.tight_layout()
        plt.savefig(GRAPH_OUTPUT_DIR / f"language_{language}_{status}_line.png", dpi=300)
        plt.close()


def create_language_bar_graph(language, data, status):
    """Create a bar chart for a specific language and status."""
    # Get frequencies for this status
    freqs = data[status]

    if not freqs:
        return  # Skip if no data for this status

    # Sort actions by frequency descending
    sorted_actions = sorted(freqs.items(), key=lambda x: x[1], reverse=True)

    plt.figure(figsize=(14, 8))

    # Extract actions and frequencies for plotting
    actions = [action for action, _ in sorted_actions]
    frequencies = [freq for _, freq in sorted_actions]

    # Create horizontal bar chart
    bars = plt.barh(actions, frequencies)

    # Add percentage labels
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 1, bar.get_y() + bar.get_height() / 2, f"{width:.1f}%", va="center")

    # Add styling
    plt.xlabel("Frequency (%)")
    plt.title(f"Action Frequency for {language.capitalize()} - {status.capitalize()}")
    plt.tight_layout()

    plt.savefig(GRAPH_OUTPUT_DIR / f"language_{language}_{status}_bar.png", dpi=300)
    plt.close()


def create_language_comparison_graph(language_data, all_actions):
    """Create a comparison graph for action types across languages."""
    if not language_data:
        print("No valid language data for comparison graph.")
        return

    # Get the top 5 most common actions across all languages
    action_totals = Counter()
    for lang, data in language_data.items():
        for action, freq in data["passed"].items():
            weight = freq * data["total_passed"] / 100 if data["total_passed"] > 0 else 0
            action_totals[action] += weight
        for action, freq in data["failed"].items():
            weight = freq * data["total_failed"] / 100 if data["total_failed"] > 0 else 0
            action_totals[action] += weight

    top_actions = [action for action, _ in action_totals.most_common(5)]

    # For each top action, create percentile distribution graph across languages
    for action in top_actions:
        plt.figure(figsize=(14, 8))

        # Collect all frequencies for this action (passed and failed)
        passed_freqs = []
        failed_freqs = []

        for language, data in language_data.items():
            # Get per-trajectory percentages if available
            if action in data["trajectory_percentages"]["passed"] and data["trajectory_percentages"]["passed"][action]:
                passed_freqs.extend(data["trajectory_percentages"]["passed"][action])

            if action in data["trajectory_percentages"]["failed"] and data["trajectory_percentages"]["failed"][action]:
                failed_freqs.extend(data["trajectory_percentages"]["failed"][action])

        # Define percentile range for x-axis
        percentiles = np.linspace(0, 100, 101)  # 0 to 100 percentiles

        # Plot passed trajectory percentiles if we have enough data
        if len(passed_freqs) >= 5:
            # Calculate percentile values
            percentile_values = [np.percentile(passed_freqs, p) for p in percentiles]

            # Plot the line
            plt.plot(percentiles, percentile_values, label="Passed", linewidth=2, color="blue")

            # Add a marker at the median value
            median_value = np.median(passed_freqs)
            plt.scatter(50, median_value, s=80, zorder=5, color="blue")

            # Add a text label at the end of the line
            plt.text(101, percentile_values[-1], "Passed", fontsize=9, verticalalignment="center")

        # Plot failed trajectory percentiles if we have enough data
        if len(failed_freqs) >= 5:
            # Calculate percentile values
            percentile_values = [np.percentile(failed_freqs, p) for p in percentiles]

            # Plot the line
            plt.plot(percentiles, percentile_values, label="Failed", linewidth=2, color="blue", linestyle="--")

            # Add a marker at the median value
            median_value = np.median(failed_freqs)
            plt.scatter(50, median_value, s=80, zorder=5, color="blue")

            # Add a text label at the end of the line
            plt.text(101, percentile_values[-1], "Failed", fontsize=9, verticalalignment="center")

        # Fall back to bar chart if not enough data for either passed or failed
        if len(passed_freqs) < 5 and len(failed_freqs) < 5:
            plt.close()
            create_action_comparison_bar_chart(language_data, action)
            continue

        # Add graph styling
        plt.xlabel("Percentile")
        plt.ylabel("Frequency (%)")
        plt.title(f"Distribution of '{action}' Action Across All Languages")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()

        plt.savefig(GRAPH_OUTPUT_DIR / f"action_{action}_language_comparison.png", dpi=300)
        plt.close()


def create_action_comparison_bar_chart(language_data, action):
    """Create a bar chart comparing a specific action across languages."""
    # Collect data for languages that have this action
    data_to_plot = []

    for language, data in language_data.items():
        passed = data["passed"].get(action, 0)
        failed = data["failed"].get(action, 0)

        # Only include languages with data for this action
        if passed > 0 or failed > 0:
            data_to_plot.append({"language": language, "passed": passed, "failed": failed, "total": passed + failed})

    if not data_to_plot:
        return

    # Sort by total frequency
    data_to_plot.sort(key=lambda x: x["total"], reverse=True)

    # Extract data for plotting
    languages = [item["language"] for item in data_to_plot]
    passed_values = [item["passed"] for item in data_to_plot]
    failed_values = [item["failed"] for item in data_to_plot]

    # Create the plot
    plt.figure(figsize=(14, 8))
    x = list(range(len(languages)))
    width = 0.35

    plt.bar([i - width / 2 for i in x], passed_values, width, label="Passed", color="green")
    plt.bar([i + width / 2 for i in x], failed_values, width, label="Failed", color="red")

    plt.xlabel("Language")
    plt.ylabel("Frequency (%)")
    plt.title(f"'{action}' Action Frequency by Language")
    plt.xticks(x, [lang.capitalize() for lang in languages], rotation=45)
    plt.legend()
    plt.tight_layout()

    plt.savefig(GRAPH_OUTPUT_DIR / f"action_{action}_language_comparison_bar.png", dpi=300)
    plt.close()


def get_action_type(action_str):
    """Determine the type of action based on the action string."""
    action_lower = action_str.lower()

    if action_lower.startswith(("find", "grep")):
        return "Find or grep"
    elif action_lower.startswith("str_replace_editor view"):
        return "View file"
    elif action_lower.startswith("str_replace_editor str_replace"):
        return "Edit file"
    elif action_lower.startswith("str_replace_editor create"):
        return "Create file"
    elif action_lower.startswith("submit"):
        return "Submit"
    else:
        return "Bash"


if __name__ == "__main__":
    analyze_trajectories()

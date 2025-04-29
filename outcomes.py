#!/usr/bin/env python3
import concurrent.futures
import glob
import mmap
import os
import sys
from pathlib import Path
import argparse


def check_log_file(log_path):
    """
    Check a log file for specific patterns and return the result.
    Uses memory mapping for efficient reading of large files.
    Returns all detected outcomes to identify conflicting situations.
    """
    # List to store all matching outcomes
    detected_outcomes = []

    try:
        with open(log_path, "rb") as f:
            # Memory map the file for faster searching
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                # Check for conflicts between "Submitted successfully" and "Exit due to cost limit"
                submission_pos = mm.find(b"<<SWE_AGENT_SUBMISSION>>")
                cost_limit_pos = mm.find(b"Exit due to cost limit")

                # Handle both outcomes based on their presence and position
                if submission_pos != -1 and cost_limit_pos != -1:
                    # When both are present, the later one takes precedence
                    detected_outcomes.append(
                        "Submitted successfully" if submission_pos > cost_limit_pos else "Exit due to cost limit"
                    )
                elif submission_pos != -1:
                    detected_outcomes.append("Submitted successfully")
                elif cost_limit_pos != -1:
                    detected_outcomes.append("Exit due to cost limit")

                # Check for other error conditions
                if mm.find(b"Exit due to repeated format/blocklist/bash syntax errors") != -1:
                    detected_outcomes.append("Exit due to repeated format/blocklist/bash syntax errors")
                if mm.find(b"input length and `max_tokens` exceed context limit") != -1:
                    detected_outcomes.append("Context limit exceeded")
                if mm.find(b"Exit due to multiple consecutive command timeouts") != -1:
                    detected_outcomes.append("Multiple consecutive command timeouts")
                if mm.find(b"cannot schedule new futures after shutdown") != -1:
                    detected_outcomes.append("Interrupted early")

                # Check for Docker build error in the last 20 lines
                file_size = os.path.getsize(log_path)
                # Read the last ~20 lines (approximate by reading last 4KB)
                last_chunk_size = min(4096, file_size)
                mm.seek(max(0, file_size - last_chunk_size))
                last_chunk = mm.read(last_chunk_size)

                if b"Command '['docker', 'build', '-q', '--build-arg'" in last_chunk:
                    detected_outcomes.append("Docker build error")

                # If no patterns were found, mark as "Other"
                if not detected_outcomes:
                    detected_outcomes.append("Other")

                # If multiple outcomes detected (excluding the handled conflict), consider it a conflicting case
                if len(detected_outcomes) > 1:
                    return f"{log_path}: CONFLICT - {' + '.join(detected_outcomes)}"
                else:
                    return f"{log_path}: {detected_outcomes[0]}"
    except Exception as e:
        return f"{log_path}: ERROR - {str(e)}"


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Analyze log files for specific outcomes.")
    parser.add_argument("directory", help="Directory path containing log files")
    parser.add_argument("--count", action="store_true", help="Print only the counts, not individual filenames")
    args = parser.parse_args()

    dir_path = args.directory

    # Find all matching log files
    log_pattern = os.path.join(dir_path, "*", "*.trace.log")
    log_files = glob.glob(log_pattern)

    if not log_files:
        print(f"No log files found matching pattern: {log_pattern}")
        sys.exit(0)

    print(f"Found {len(log_files)} log files to analyze.")

    # Group to store results by outcome (using display names directly)
    results_by_outcome = {
        "Submitted successfully": [],
        "Exit due to cost limit": [],
        "Exit due to repeated format/blocklist/bash syntax errors": [],
        "Context limit exceeded": [],
        "Docker build error": [],
        "Multiple consecutive command timeouts": [],
        "Interrupted early": [],
        "Other": [],  # For files with no matching patterns
        "CONFLICT": [],  # Category for conflicting outcomes
    }

    # Process files in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(check_log_file, log_files))

        # Group results by outcome
        for result in results:
            full_path, outcome = result.split(": ", 1)
            filename = os.path.basename(full_path).replace(".info.log", "")

            # Handle error and conflict cases
            if outcome.startswith("ERROR"):
                if "ERROR" not in results_by_outcome:
                    results_by_outcome["ERROR"] = []
                results_by_outcome["ERROR"].append(filename)
            elif outcome.startswith("CONFLICT"):
                results_by_outcome["CONFLICT"].append(f"{filename} ({outcome[10:]})")  # Include conflict details
            else:
                results_by_outcome[outcome].append(filename)

    if args.count:
        # In count mode, use compact format with aligned counts
        total = 0
        max_name_length = max(len(outcome) for outcome in results_by_outcome.keys())
        if results_by_outcome.get("ERROR"):
            max_name_length = max(max_name_length, len("ERROR"))

        for outcome, files in results_by_outcome.items():
            count = len(files)
            if count > 0:  # Only print outcomes with at least one file
                total += count
                print(f"{outcome:{max_name_length}}: {count}")

        # Print errors count if any
        if results_by_outcome.get("ERROR") and len(results_by_outcome["ERROR"]) > 0:
            error_count = len(results_by_outcome["ERROR"])
            total += error_count
            print(f"{'ERROR':{max_name_length}}: {error_count}")

        # Print total
        print(f"{'':-<{max_name_length + 2}}")  # Separator line
        print(f"{'Total':{max_name_length}}: {total}")
    else:
        # Original verbose output with individual filenames
        for outcome, files in results_by_outcome.items():
            if len(files) > 0:  # Only print outcomes with at least one file
                print(f"\n{outcome}:")
                print(f"Count: {len(files)}")
                for filename in sorted(files):
                    print(f"  {filename}")

        # Print errors if any
        if results_by_outcome.get("ERROR") and len(results_by_outcome["ERROR"]) > 0:
            print("\nERROR:")
            print(f"Count: {len(results_by_outcome['ERROR'])}")
            for filename in sorted(results_by_outcome["ERROR"]):
                print(f"  {filename}")


if __name__ == "__main__":
    main()

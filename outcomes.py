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
    """
    # Use display names directly as the result
    result = "Other"  # Default outcome (previously "None")

    try:
        with open(log_path, "rb") as f:
            # Memory map the file for faster searching
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                # Check for "Exit due to cost limit"
                if mm.find(b"Exit due to cost limit") != -1:
                    result = "Exit due to cost limit"
                # Check for "Exit due to repeated format/blocklist/bash syntax errors"
                elif mm.find(b"Exit due to repeated format/blocklist/bash syntax errors") != -1:
                    result = "Exit due to repeated format/blocklist/bash syntax errors"
                # Check for context limit exceeded
                elif mm.find(b"input length and `max_tokens` exceed context limit") != -1:
                    result = "Context limit exceeded"
                # Check for "🎬 ACTION\nsubmit"
                elif mm.find(b"\xf0\x9f\x8e\xac ACTION\nsubmit") != -1:
                    result = "Submitted successfully"  # Use display name directly
                # Check for Docker build error in the last 20 lines
                else:
                    # Reset to the end and read the last part of the file
                    file_size = os.path.getsize(log_path)
                    # Read the last ~20 lines (approximate by reading last 4KB)
                    last_chunk_size = min(4096, file_size)
                    mm.seek(max(0, file_size - last_chunk_size))
                    last_chunk = mm.read(last_chunk_size)

                    if b"Command '['docker', 'build', '-q', '--build-arg'" in last_chunk:
                        result = "Docker build error"
    except Exception as e:
        return f"{log_path}: ERROR - {str(e)}"

    return f"{log_path}: {result}"


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Analyze log files for specific outcomes.")
    parser.add_argument("directory", help="Directory path containing log files")
    parser.add_argument("--count", action="store_true", help="Print only the counts, not individual filenames")
    args = parser.parse_args()

    dir_path = args.directory

    # Find all matching log files
    log_pattern = os.path.join(dir_path, "*", "*.info.log")
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
        "Other": [],  # For files with no matching patterns
    }

    # Process files in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(check_log_file, log_files))

        # Group results by outcome
        for result in results:
            full_path, outcome = result.split(": ", 1)
            filename = os.path.basename(full_path).replace(".info.log", "")

            # Handle error cases
            if outcome.startswith("ERROR"):
                if "ERROR" not in results_by_outcome:
                    results_by_outcome["ERROR"] = []
                results_by_outcome["ERROR"].append(filename)
            else:
                results_by_outcome[outcome].append(filename)

    # Print results in the specified order
    outcome_order = [
        "Submitted successfully",
        "Exit due to cost limit",
        "Exit due to repeated format/blocklist/bash syntax errors",
        "Context limit exceeded",
        "Docker build error",
        "Other",
    ]

    if args.count:
        # In count mode, use compact format with aligned counts
        total = 0
        max_name_length = max(len(outcome) for outcome in outcome_order)
        if results_by_outcome.get("ERROR"):
            max_name_length = max(max_name_length, len("ERROR"))

        for outcome in outcome_order:
            files = results_by_outcome[outcome]
            count = len(files)
            total += count
            print(f"{outcome:{max_name_length}}: {count}")

        # Print errors count if any
        if results_by_outcome.get("ERROR"):
            error_count = len(results_by_outcome["ERROR"])
            total += error_count
            print(f"{'ERROR':{max_name_length}}: {error_count}")

        # Print total
        print(f"{'':-<{max_name_length + 2}}")  # Separator line
        print(f"{'Total':{max_name_length}}: {total}")
    else:
        # Original verbose output with individual filenames
        for outcome in outcome_order:
            files = results_by_outcome[outcome]
            print(f"\n{outcome}:")
            print(f"Count: {len(files)}")
            for filename in sorted(files):
                print(f"  {filename}")

        # Print errors if any
        if results_by_outcome.get("ERROR"):
            print("\nERROR:")
            print(f"Count: {len(results_by_outcome['ERROR'])}")
            for filename in sorted(results_by_outcome["ERROR"]):
                print(f"  {filename}")


if __name__ == "__main__":
    main()

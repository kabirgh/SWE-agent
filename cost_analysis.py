#!/usr/bin/env python3
import concurrent.futures
import glob
import json
import mmap
import os
import sys
from pathlib import Path
import argparse


def check_log_file(log_path):
    """
    Check a log file for cost limit exit pattern.
    Uses memory mapping for efficient reading of large files.
    """
    try:
        with open(log_path, "rb") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                # Check for "Exit due to cost limit"
                cost_limit_pos = mm.find(b"Exit due to cost limit")
                submission_pos = mm.find(b"<<SWE_AGENT_SUBMISSION>>")

                # Only return True if cost limit is the final outcome
                if cost_limit_pos != -1:
                    if submission_pos == -1 or cost_limit_pos > submission_pos:
                        return True
        return False
    except Exception as e:
        print(f"Error processing {log_path}: {str(e)}", file=sys.stderr)
        return False


def extract_instance_id(log_path):
    """Extract the instance ID from the log file path."""
    # Assuming log path format: .../instance_id/something.trace.log
    return Path(log_path).parent.name


def main():
    parser = argparse.ArgumentParser(description="Extract instances that hit cost limits.")
    parser.add_argument("directory", help="Directory path containing log files")
    parser.add_argument("--instances", default="instances.jsonl", help="Path to instances.jsonl file")
    parser.add_argument("--output", default="cost.jsonl", help="Output file for cost-limited instances")
    args = parser.parse_args()

    # Find all matching log files
    log_pattern = os.path.join(args.directory, "*", "*.trace.log")
    log_files = glob.glob(log_pattern)

    if not log_files:
        print(f"No log files found matching pattern: {log_pattern}")
        sys.exit(0)

    print(f"Found {len(log_files)} log files to analyze.")

    # Process files in parallel to find cost-limited ones
    cost_limited_instances = set()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for log_file, is_cost_limited in zip(log_files, executor.map(check_log_file, log_files)):
            if is_cost_limited:
                instance_id = extract_instance_id(log_file)
                cost_limited_instances.add(instance_id)

    print(f"Found {len(cost_limited_instances)} instances that hit cost limits.")

    # Read original instances and write cost-limited ones to new file
    written_count = 0
    with open(args.instances, "r", encoding="utf-8") as infile, open(args.output, "w", encoding="utf-8") as outfile:
        for line in infile:
            instance = json.loads(line)
            if instance.get("instance_id") in cost_limited_instances:
                outfile.write(line)
                written_count += 1

    print(f"Wrote {written_count} instances to {args.output}")


if __name__ == "__main__":
    main()

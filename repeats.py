import hashlib
from collections import defaultdict
import argparse


def detect_repeated_groups(file_path, group_size=20, similarity_threshold=0.9):
    groups = defaultdict(list)
    current_group = []

    with open(file_path, "r") as file:
        for line_number, line in enumerate(file, 1):
            current_group.append(line.strip())

            if len(current_group) == group_size:
                group_hash = hashlib.md5("".join(current_group).encode()).hexdigest()
                groups[group_hash].append((line_number - group_size + 1, line_number))
                current_group.pop(0)

    repeated_groups = {k: v for k, v in groups.items() if len(v) > 1}

    print(f"Found {len(repeated_groups)} repeated groups:")
    for hash_value, occurrences in repeated_groups.items():
        print(f"\nGroup hash: {hash_value}")
        print(f"Occurrences: {occurrences}")
        print("Sample lines:")
        with open(file_path, "r") as file:
            for _ in range(occurrences[0][0] - 1):
                next(file)
            for _ in range(group_size):
                print(next(file).strip())


# Add this new function to set up command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Detect repeated groups in a log file.")
    parser.add_argument("file_path", help="Path to the log file")
    parser.add_argument("-s", "--group-size", type=int, default=20, help="Size of the groups to check (default: 20)")
    parser.add_argument("-t", "--threshold", type=float, default=0.9, help="Similarity threshold (default: 0.9)")
    return parser.parse_args()


# Replace the usage section with this
if __name__ == "__main__":
    args = parse_arguments()
    detect_repeated_groups(args.file_path, args.group_size, args.threshold)

import os
import re


def find_failed_instances(log_directory):
    # Regular expressions for matching relevant log lines
    start_pattern = re.compile(r"Trajectory will be saved to trajectories/root/.*?/(.+)\.traj")
    fail_pattern = re.compile(r"Cost limit exceeded")
    failed_instances = []

    # Iterate through all files in the directory
    for filename in os.listdir(log_directory):
        if filename.endswith(".log"):
            file_path = os.path.join(log_directory, filename)
            current_instance = None

            with open(file_path, "r") as file:
                for line in file:
                    # Check for instance start
                    start_match = start_pattern.search(line)
                    if start_match:
                        current_instance = start_match.group(1)

                    # Check for failure
                    if current_instance and fail_pattern.search(line):
                        failed_instances.append(current_instance)
                        current_instance = None  # Reset for the next instance

    print(f"({'|'.join(failed_instances)})")


# Specify the directory containing the log files
log_directory = "trajectories/root/gpt-4o-2024-08-06__sbm__default__t-0.00__p-0.95__c-1.00__install-1"

# Call the function to find and print failed instances
find_failed_instances(log_directory)

import os
import json
import sys


def print_instance_costs(folder_path, *json_filenames):
    instance_costs = []

    for filename in json_filenames:
        # Ensure the filename ends with .traj
        if not filename.endswith(".traj"):
            filename += ".traj"

        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                instance_cost = data.get("info", {}).get("model_stats", {}).get("instance_cost")
                if instance_cost is not None:
                    print(f"{filename}: {instance_cost}")
                    instance_costs.append(instance_cost)
                else:
                    print(f"{filename}: 'instance_cost' not found")
        except FileNotFoundError:
            print(f"{filename}: File not found")
        except json.JSONDecodeError:
            print(f"{filename}: Error decoding JSON")

    if instance_costs:
        min_cost = min(instance_costs)
        max_cost = max(instance_costs)
        avg_cost = sum(instance_costs) / len(instance_costs)
        print(f"Min: {min_cost}, Average: {avg_cost}, Max: {max_cost}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <folder_path> <json_file1> <json_file2> ...")
    else:
        folder_path = sys.argv[1]
        json_filenames = sys.argv[2:]
        print_instance_costs(folder_path, *json_filenames)

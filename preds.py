#!/usr/bin/env python3
import concurrent.futures
import glob
import os
import sys
from pathlib import Path
import argparse


def read_pred_file(pred_path):
    """
    Read a prediction file and return its contents.
    """
    try:
        with open(pred_path, "r", encoding="utf-8") as f:
            content = f.read()
        return pred_path, content
    except Exception as e:
        return pred_path, f"ERROR - {str(e)}"


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Concatenate .pred files into a single output file.")
    parser.add_argument("directory", help="Directory path containing .pred files")
    parser.add_argument("output_file", help="Path to the output file where predictions will be concatenated")
    parser.add_argument("--count", action="store_true", help="Print only the count of files processed")
    args = parser.parse_args()

    dir_path = args.directory
    output_path = args.output_file

    # Find all matching .pred files
    pred_pattern = os.path.join(dir_path, "**", "*.pred")
    pred_files = glob.glob(pred_pattern, recursive=True)

    if not pred_files:
        print(f"No .pred files found matching pattern: {pred_pattern}")
        sys.exit(0)

    # Sort the pred files alphabetically by filename
    pred_files.sort()

    file_count = len(pred_files)
    print(f"Found {file_count} .pred files to concatenate.")

    # Store errors for reporting
    errors = []

    # Open output file for writing
    with open(output_path, "w", encoding="utf-8") as out_file:
        # Process files in parallel
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = list(executor.map(read_pred_file, pred_files))

            # Write contents to output file
            for pred_path, content in results:
                if content.startswith("ERROR"):
                    errors.append((pred_path, content))
                    continue

                out_file.write(content + "\n")

    # Report statistics
    if args.count:
        # Print simple count and errors
        print(f"Successfully concatenated {file_count - len(errors)} files to {output_path}")
        if errors:
            print(f"Failed to process {len(errors)} files")
    else:
        # More detailed output
        print(f"\nSuccessfully concatenated {file_count - len(errors)} files to {output_path}")

        # Print errors if any
        if errors:
            print(f"\nErrors encountered ({len(errors)}):")
            for path, error in errors:
                print(f"  {path}: {error}")


if __name__ == "__main__":
    main()

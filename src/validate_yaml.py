import os
import yaml
import sys

def validate_yaml(file_path, count, total_files, failed_flag):
    try:
        with open(file_path, 'r') as file:
            yaml.safe_load(file)
        print(f"Validation passed for {file_path} ({count}/{total_files})")
    except Exception as e:
        print(f"Validation failed for {file_path}: {str(e)} ({count}/{total_files})")
        failed_flag[0] = True

if __name__ == '__main':
    if len(sys.argv) != 2:
        print("Usage: python validate_yaml.py <directory_path>")
        sys.exit(1)

    directory_path = sys.argv[1]
    if not os.path.exists(directory_path):
        print(f"Validation failed: Directory {directory_path} not found.")
        sys.exit(1)

    # Get the list of YAML and YML files to be processed
    yaml_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.lower().endswith(('.yaml', '.yml'))]

    total_files = len(yaml_files)
    failed_flag = [False]

    for count, yaml_file in enumerate(yaml_files, start=1):
        validate_yaml(yaml_file, count, total_files, failed_flag)

    if failed_flag[0]:
        sys.exit(1)

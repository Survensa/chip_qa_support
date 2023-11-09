import os
import yaml
import sys

def validate_yaml(file_path, count, total_files, failed_flag):
    try:
        with open(file_path, 'r') as file:
            yaml.safe_load(file)
        print(f"YAML syntax is valid in {file_path} ({count}/{total_files})")
    except yaml.YAMLError as e:
        print(f"Error in {file_path} ({count}/{total_files}): {e}")
        failed_flag[0] = True

def check_yaml_files(folder_path):
    yaml_files = [filename for filename in os.listdir(folder_path) if filename.endswith((".yaml", ".yml"))]
    total_files = len(yaml_files)
    failed_flag = [False]

    for count, yaml_file in enumerate(yaml_files, start=1):
        file_path = os.path.join(folder_path, yaml_file)
        validate_yaml(file_path, count, total_files, failed_flag)

    if failed_flag[0]:
        sys.exit(1)

if __name__ == "__main__":
    folder_to_check = "command"
    check_yaml_files(folder_to_check)

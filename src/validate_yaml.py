import os
import yaml
import sys
import glob

def validate_yaml(file_path, count, total_files, failed_flag):
    try:
        with open(file_path, 'r') as file:
            yaml.safe_load(file)
        print(f"Validation passed for {file_path} ({count}/{total_files})")
    except Exception as e:
        print(f"Validation failed for {file_path}: {str(e)} ({count}/{total_files})")
        failed_flag[0] = True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python validate_yaml.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Validation failed: File {file_path} not found.")
        sys.exit(1)

    # Get the list of YAML files to be processed (both .yaml and .yml)
    yaml_files = glob.glob(os.path.join(os.path.dirname(file_path), '*.[yY][aA][mM][lL]')

    total_files = len(yaml_files)
    failed_flag = [False]

    for count, yaml_file in enumerate(yaml_files, start=1):
        validate_yaml(yaml_file, count, total_files, failed_flag)

    if failed_flag[0]:
        sys.exit(1)

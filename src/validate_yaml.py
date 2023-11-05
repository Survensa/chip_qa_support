import yaml
import sys

def validate_yaml(file_path):
    try:
        with open(file_path, 'r') as file:
            yaml.safe_load(file)
        print(f"Validation passed for {file_path}")
    except Exception as e:
        print(f"Validation failed for {file_path}: {str(e)}")
        return False

    return True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python validate_yaml.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    validation_status = validate_yaml(file_path)

    if not validation_status:
        sys.exit(1)
